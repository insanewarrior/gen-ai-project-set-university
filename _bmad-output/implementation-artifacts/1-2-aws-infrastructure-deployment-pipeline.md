# Story 1.2: AWS Infrastructure & Deployment Pipeline

Status: review

## Story

As an **operator**,
I want to deploy the entire StrengthWise stack to AWS with a single command and tear it down completely with another,
So that I have zero lingering resources and repeatable deployments.

## Acceptance Criteria

1. **Given** the CDK stack is defined with all required resources **When** I run `make deploy` (or `scripts/deploy.sh`) **Then** the following resources are provisioned: DynamoDB tables (Sessions, QueryUsage, Feedback), Cognito user pool, Lambda function (container image from ECR), API Gateway, S3 bucket + CloudFront distribution **And** the deployment completes without errors

2. **Given** a deployed stack exists **When** I run `make teardown` (or `scripts/teardown.sh`) **Then** all AWS resources are destroyed with zero lingering resources **And** running teardown multiple times does not produce errors (idempotent)

3. **Given** the backend Dockerfile exists **When** I build the container image **Then** it produces a working Lambda container image targeting linux/amd64 with all dependencies (FastAPI, Mangum, boto3, faiss-cpu, sentence-transformers, anthropic)

4. **Given** I run `cdk deploy` multiple times **When** the stack already exists **Then** deployment is idempotent — no errors or resource duplication (NFR27)

## Tasks / Subtasks

- [x] Task 1: Create backend Dockerfile for Lambda container (AC: #3)
  - [x] 1.1: Create `backend/Dockerfile` — multi-stage build: stage 1 installs Python deps (faiss-cpu, sentence-transformers, FastAPI, boto3, anthropic, mangum), stage 2 copies app code + deps into Lambda Python base image
  - [x] 1.2: Target `--platform linux/amd64` (required even on Apple Silicon)
  - [x] 1.3: Update `backend/requirements.txt` to include all production deps: fastapi, mangum==0.21.0, uvicorn, boto3, pydantic, faiss-cpu, sentence-transformers, anthropic
  - [x] 1.4: Verify local Docker build succeeds: `docker build --platform linux/amd64 -t strengthwise-backend ./backend`

- [x] Task 2: Implement CDK stack — DynamoDB tables (AC: #1, #4)
  - [x] 2.1: Add DynamoDB Sessions table (PK: `userId` String, SK: `sessionDate#sessionId` String, on-demand billing, removal_policy DESTROY)
  - [x] 2.2: Add DynamoDB QueryUsage table (PK: `userId` String, SK: `date` String, on-demand billing, removal_policy DESTROY)
  - [x] 2.3: Add DynamoDB Feedback table (PK: `queryId` String, no SK, on-demand billing, removal_policy DESTROY)

- [x] Task 3: Implement CDK stack — Cognito user pool (AC: #1)
  - [x] 3.1: Add Cognito user pool with email sign-in, self sign-up enabled, email verification
  - [x] 3.2: Add Cognito user pool client (no client secret for SPA, auth flows: USER_SRP_AUTH, ALLOW_REFRESH_TOKEN_AUTH)
  - [x] 3.3: Output user pool ID and client ID as CfnOutput for frontend config

- [x] Task 4: Implement CDK stack — Lambda function from Docker image (AC: #1, #3)
  - [x] 4.1: Use `aws_lambda.DockerImageFunction` with `DockerImageCode.from_image_asset(directory="backend")` — CDK handles build+push to ECR automatically
  - [x] 4.2: Configure Lambda: 512MB memory, 30s timeout, `--platform linux/amd64`
  - [x] 4.3: Set environment variables on Lambda: table names, FAISS_INDEX_PATH, CLAUDE_MODEL, S3 bucket name for FAISS index
  - [x] 4.4: Grant Lambda read/write permissions on all 3 DynamoDB tables
  - [x] 4.5: Grant Lambda read permissions on S3 bucket (for FAISS index in later stories)

- [x] Task 5: Implement CDK stack — API Gateway (AC: #1)
  - [x] 5.1: Add API Gateway REST API or HTTP API (HttpApi preferred — cheaper, simpler)
  - [x] 5.2: Add Lambda integration as the default route handler (`$default` → Lambda)
  - [x] 5.3: Configure CORS on API Gateway to allow CloudFront origin
  - [x] 5.4: Output API Gateway endpoint URL as CfnOutput

- [x] Task 6: Implement CDK stack — S3 + CloudFront for frontend (AC: #1)
  - [x] 6.1: Add S3 bucket for frontend static assets (block public access, removal_policy DESTROY, auto_delete_objects True)
  - [x] 6.2: Add CloudFront distribution with S3 origin (OAI/OAC for private bucket access)
  - [x] 6.3: Configure CloudFront default root object (`index.html`), custom error responses for SPA routing (403/404 → /index.html with 200)
  - [x] 6.4: Output CloudFront distribution URL as CfnOutput

- [x] Task 7: Implement CDK stack — S3 bucket for FAISS index (AC: #1)
  - [x] 7.1: Add S3 bucket for FAISS index storage (removal_policy DESTROY, auto_delete_objects True)
  - [x] 7.2: Grant Lambda read access to this bucket
  - [x] 7.3: Pass bucket name to Lambda as environment variable

- [x] Task 8: Implement deploy.sh script (AC: #1, #4)
  - [x] 8.1: Build frontend: `cd frontend && npm ci && npm run build`
  - [x] 8.2: CDK deploy: `cd infra && cdk deploy --require-approval never`
  - [x] 8.3: Upload frontend dist/ to S3 (extract bucket name from CDK outputs)
  - [x] 8.4: CloudFront invalidation: `aws cloudfront create-invalidation`
  - [x] 8.5: Ensure idempotent — running multiple times produces no errors

- [x] Task 9: Implement teardown.sh script (AC: #2)
  - [x] 9.1: CDK destroy: `cd infra && cdk destroy --force`
  - [x] 9.2: Ensure idempotent — running on already-destroyed stack produces no errors

- [x] Task 10: Add teardown target to Makefile
  - [x] 10.1: Add `teardown` target pointing to `scripts/teardown.sh`

- [x] Task 11: Update config.py with new env vars (AC: #1)
  - [x] 11.1: Add `SESSIONS_TABLE_NAME`, `QUERY_USAGE_TABLE_NAME`, `FEEDBACK_TABLE_NAME` env vars with defaults for local dev
  - [x] 11.2: Add `S3_FAISS_BUCKET` env var (None for local dev, set by CDK for Lambda)
  - [x] 11.3: Update `.env.example` with new variables

- [x] Task 12: Validate CDK synth and deployment readiness
  - [x] 12.1: Run `cdk synth` and verify valid CloudFormation template with all resources
  - [x] 12.2: Verify all CfnOutputs are present (API URL, CloudFront URL, User Pool ID, Client ID, S3 bucket names)

## Dev Notes

### Architecture Compliance

**CRITICAL — Follow the architecture document exactly. Do not deviate from these patterns:**

- **IaC:** AWS CDK v2 in Python. Single stack (`StrengthwiseStack`). All resources in one stack.
- **Lambda deployment:** Docker container image, NOT a ZIP package. FAISS + sentence-transformers exceeds ZIP size limits (~500MB total). CDK's `DockerImageFunction` with `DockerImageCode.from_image_asset()` handles build+push to ECR automatically — do NOT manually create an ECR repository or push images.
- **DynamoDB:** On-demand billing mode (no provisioned capacity). `removal_policy=RemovalPolicy.DESTROY` on all tables so `cdk destroy` cleans up everything.
- **S3 buckets:** `removal_policy=RemovalPolicy.DESTROY` and `auto_delete_objects=True` on all buckets. Without `auto_delete_objects`, `cdk destroy` fails on non-empty buckets.
- **Idempotency:** CDK is inherently idempotent — repeated `cdk deploy` only updates changed resources. The deploy.sh script must also be idempotent (NFR27).

### CDK Stack Structure

The entire stack goes in `infra/stacks/strengthwise_stack.py`. Use CDK L2 constructs (not L1 Cfn* constructs) for cleaner code. Import pattern:

```python
from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    Duration,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigatewayv2 as apigwv2,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_cognito as cognito,
)
```

### DynamoDB Table Design (from Architecture)

| Table | PK | SK | Notes |
|-------|----|----|-------|
| `Sessions` | `userId` (S) | `sessionDate#sessionId` (S) | Composite sort key for date ordering |
| `QueryUsage` | `userId` (S) | `date` (S) | Daily counter for rate limiting |
| `Feedback` | `queryId` (S) | — | No sort key, simple key-value |

All tables use `billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST` (on-demand).

### Lambda Configuration

```python
lambda_.DockerImageFunction(
    self, "BackendFunction",
    code=lambda_.DockerImageCode.from_image_asset(
        directory="../backend",
        platform=ecr_assets.Platform.LINUX_AMD64,
    ),
    memory_size=512,
    timeout=Duration.seconds(30),
    environment={
        "SESSIONS_TABLE_NAME": sessions_table.table_name,
        "QUERY_USAGE_TABLE_NAME": query_usage_table.table_name,
        "FEEDBACK_TABLE_NAME": feedback_table.table_name,
        "FAISS_INDEX_PATH": "/tmp/faiss_index",
        "S3_FAISS_BUCKET": faiss_bucket.bucket_name,
        "CLAUDE_MODEL": "claude-sonnet-4-5-20250514",
    },
)
```

Use `from aws_cdk.aws_ecr_assets import Platform` for the `platform` parameter. The `directory` path is relative to where `cdk deploy` runs (the `infra/` directory), so use `../backend`.

### Backend Dockerfile Pattern

Multi-stage build targeting Lambda Python runtime:

```dockerfile
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.12 AS builder

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -t /opt/python

FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.12

COPY --from=builder /opt/python ${LAMBDA_TASK_ROOT}
COPY . ${LAMBDA_TASK_ROOT}

CMD ["main.handler"]
```

The Lambda entry point is `main.handler` — this is the Mangum handler already defined in `backend/main.py`:
```python
handler = Mangum(app)  # Lambda entry point
```

### API Gateway

Use HTTP API (ApiGatewayV2) — cheaper and simpler than REST API. For the MVP, a single `$default` route that proxies everything to Lambda is sufficient. FastAPI handles all routing internally.

```python
from aws_cdk import aws_apigatewayv2 as apigwv2
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration

api = apigwv2.HttpApi(self, "HttpApi",
    cors_preflight=apigwv2.CorsPreflightOptions(
        allow_origins=["*"],  # Tighten to CloudFront URL post-deploy
        allow_methods=[apigwv2.CorsHttpMethod.ANY],
        allow_headers=["*"],
    ),
)
integration = HttpLambdaIntegration("LambdaIntegration", backend_function)
api.add_routes(route_key=apigwv2.HttpRouteKey.with_("/{proxy+}", apigwv2.HttpMethod.ANY), integration=integration)
api.add_routes(route_key=apigwv2.HttpRouteKey.with_("/", apigwv2.HttpMethod.ANY), integration=integration)
```

### CloudFront + S3 for Frontend

Use Origin Access Control (OAC) — OAI is legacy. Configure SPA routing with custom error responses:

```python
distribution = cloudfront.Distribution(self, "FrontendDist",
    default_behavior=cloudfront.BehaviorOptions(
        origin=origins.S3BucketOrigin.with_origin_access_control(frontend_bucket),
    ),
    default_root_object="index.html",
    error_responses=[
        cloudfront.ErrorResponse(
            http_status=403,
            response_http_status=200,
            response_page_path="/index.html",
        ),
        cloudfront.ErrorResponse(
            http_status=404,
            response_http_status=200,
            response_page_path="/index.html",
        ),
    ],
)
```

### Cognito User Pool

```python
user_pool = cognito.UserPool(self, "UserPool",
    self_sign_up_enabled=True,
    sign_in_aliases=cognito.SignInAliases(email=True),
    auto_verify=cognito.AutoVerifiedAttrs(email=True),
    removal_policy=RemovalPolicy.DESTROY,
)
client = user_pool.add_client("WebClient",
    auth_flows=cognito.AuthFlow(user_srp=True),
    o_auth=cognito.OAuthSettings(
        flows=cognito.OAuthFlows(implicit_code_grant=True),
    ),
)
```

No client secret for SPA clients. Output pool ID and client ID for frontend configuration in Story 1.3.

### deploy.sh Script

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 1. Build frontend
echo "Building frontend..."
cd "$PROJECT_ROOT/frontend"
npm ci
npm run build

# 2. CDK deploy (builds Docker image + deploys all resources)
echo "Deploying CDK stack..."
cd "$PROJECT_ROOT/infra"
pip install -r requirements.txt -q
cdk deploy --require-approval never --outputs-file cdk-outputs.json

# 3. Upload frontend to S3 (extract bucket name from CDK outputs)
BUCKET_NAME=$(python3 -c "import json; print(json.load(open('cdk-outputs.json'))['StrengthwiseStack']['FrontendBucketName'])")
echo "Uploading frontend to s3://$BUCKET_NAME..."
aws s3 sync "$PROJECT_ROOT/frontend/dist" "s3://$BUCKET_NAME" --delete

# 4. CloudFront invalidation
DIST_ID=$(python3 -c "import json; print(json.load(open('cdk-outputs.json'))['StrengthwiseStack']['DistributionId'])")
echo "Invalidating CloudFront cache..."
aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/*"

echo "Deploy complete!"
```

### teardown.sh Script

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Destroying CDK stack..."
cd "$PROJECT_ROOT/infra"
cdk destroy --force

echo "Teardown complete!"
```

### Config Changes

Add to `backend/config.py`:
```python
SESSIONS_TABLE_NAME = os.getenv("SESSIONS_TABLE_NAME", "Sessions")
QUERY_USAGE_TABLE_NAME = os.getenv("QUERY_USAGE_TABLE_NAME", "QueryUsage")
FEEDBACK_TABLE_NAME = os.getenv("FEEDBACK_TABLE_NAME", "Feedback")
S3_FAISS_BUCKET = os.getenv("S3_FAISS_BUCKET")  # None for local dev
```

Add to `.env.example`:
```
# DynamoDB table names — defaults match local dev setup
SESSIONS_TABLE_NAME=Sessions
QUERY_USAGE_TABLE_NAME=QueryUsage
FEEDBACK_TABLE_NAME=Feedback

# S3 bucket for FAISS index — leave unset for local dev
# S3_FAISS_BUCKET=
```

### infra/requirements.txt Update

The current `infra/requirements.txt` has `aws-cdk-lib>=2.100.0` and `constructs>=10.0.0`. This is sufficient. Additionally add:
```
aws-cdk-lib>=2.100.0
constructs>=10.0.0
```

You may also need `aws-cdk.aws-apigatewayv2-integrations-alpha` if using experimental HTTP API integrations, but in CDK v2.100+ the HTTP API integrations are stable in `aws_cdk.aws_apigatewayv2_integrations`. Verify the import works.

### CfnOutput Keys

Output these values for downstream scripts and stories:

| Output Key | Value | Used By |
|------------|-------|---------|
| `ApiUrl` | API Gateway endpoint URL | Frontend config (Story 1.3) |
| `CloudFrontUrl` | CloudFront distribution URL | Shared with users |
| `FrontendBucketName` | S3 bucket name | deploy.sh for frontend upload |
| `DistributionId` | CloudFront distribution ID | deploy.sh for cache invalidation |
| `UserPoolId` | Cognito user pool ID | Frontend auth config (Story 1.3) |
| `UserPoolClientId` | Cognito client ID | Frontend auth config (Story 1.3) |
| `FaissIndexBucketName` | S3 bucket for FAISS | Story 3.1 index upload |

### Previous Story Intelligence

From Story 1.1 implementation:
- Project structure already exists: `backend/`, `frontend/`, `infra/`, `scripts/`
- `infra/stacks/strengthwise_stack.py` exists as an empty shell with TODO comments — **replace the TODOs**, don't create a new file
- `scripts/deploy.sh` exists as a placeholder (echo only) — **replace the content**
- `scripts/teardown.sh` exists as a placeholder (echo only) — **replace the content**
- `backend/main.py` already has `handler = Mangum(app)` — the Lambda entry point is ready
- `backend/requirements.txt` has: fastapi, mangum==0.21.0, uvicorn, boto3, pydantic — **add** faiss-cpu, sentence-transformers, anthropic
- `backend/config.py` already has DYNAMODB_ENDPOINT, FAISS_INDEX_PATH, AUTH_BYPASS, CLAUDE_MODEL, TEST_USER_ID — **add** table name vars and S3_FAISS_BUCKET
- `infra/requirements.txt` has aws-cdk-lib>=2.100.0, constructs>=10.0.0 — sufficient
- `infra/app.py` instantiates `StrengthwiseStack` — no changes needed
- Makefile has `deploy` target pointing to `scripts/deploy.sh` — **add `teardown` target**
- Separate Python venvs for `backend/` and `infra/` — maintain this separation

### Anti-Patterns to Avoid

- Do NOT manually create an ECR repository — CDK's `DockerImageFunction` handles ECR automatically
- Do NOT use `RemovalPolicy.RETAIN` on any resource — this story requires zero lingering resources on teardown
- Do NOT forget `auto_delete_objects=True` on S3 buckets — without it, `cdk destroy` fails on non-empty buckets
- Do NOT use REST API (ApiGateway V1) — use HTTP API (ApiGatewayV2), it's cheaper and simpler
- Do NOT hardcode AWS account or region — let CDK resolve from environment/CLI config
- Do NOT add Cognito authorizer to API Gateway in this story — auth middleware is Story 1.3
- Do NOT deploy the frontend S3 content via CDK's `BucketDeployment` — use `aws s3 sync` in deploy.sh for faster iterations (BucketDeployment creates a Lambda for each deploy)
- Do NOT add uvicorn to production requirements — it's only needed for local dev. The Dockerfile should not include it unless the requirements.txt is shared (in which case it's harmless but unnecessary)

### Project Structure Notes

Files this story creates or modifies:

```
backend/
├── Dockerfile                    # NEW — multi-stage Lambda container build
├── requirements.txt              # MODIFY — add faiss-cpu, sentence-transformers, anthropic
├── config.py                     # MODIFY — add table name vars, S3_FAISS_BUCKET
├── .dockerignore                 # NEW — exclude venv, tests, __pycache__, .env

infra/
├── stacks/
│   └── strengthwise_stack.py     # MODIFY — full CDK stack implementation

scripts/
├── deploy.sh                     # MODIFY — full deploy script
├── teardown.sh                   # MODIFY — full teardown script

Makefile                          # MODIFY — add teardown target
.env.example                      # MODIFY — add new env vars
```

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Infrastructure & Deployment] — CDK single stack, container Lambda, S3+CloudFront, deployment workflow
- [Source: _bmad-output/planning-artifacts/architecture.md#Core Architectural Decisions] — DynamoDB table design, Cognito auth, API Gateway
- [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure & Boundaries] — Complete directory tree, API boundaries
- [Source: _bmad-output/planning-artifacts/architecture.md#Development Workflow] — deploy.sh and teardown.sh workflows
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.2] — Acceptance criteria, FR30, NFR27
- [Source: _bmad-output/implementation-artifacts/1-1-project-scaffold-local-dev.md] — Previous story files, patterns, and completion notes

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (1M context)

### Debug Log References

- Docker build warnings about `--platform` constant are cosmetic (intentional for Lambda amd64 target)
- CDK auto_delete_objects creates an additional Lambda function for bucket cleanup — accounted for in tests

### Completion Notes List

- Task 1: Created multi-stage Dockerfile targeting Lambda Python 3.12 on linux/amd64. Added .dockerignore. Updated requirements.txt with faiss-cpu, sentence-transformers, anthropic. Docker build verified locally.
- Tasks 2-7: Implemented full CDK stack in strengthwise_stack.py — 3 DynamoDB tables (Sessions, QueryUsage, Feedback) with PAY_PER_REQUEST billing, Cognito user pool with email sign-in, Lambda DockerImageFunction with 512MB/30s config, HTTP API Gateway with CORS and catch-all routes, S3+CloudFront for frontend (OAC, SPA error routing), S3 bucket for FAISS index. All resources use RemovalPolicy.DESTROY. 7 CfnOutputs exported.
- Task 8: Implemented deploy.sh — builds frontend, runs cdk deploy, syncs dist/ to S3, invalidates CloudFront cache. Idempotent.
- Task 9: Implemented teardown.sh — runs cdk destroy --force. Idempotent.
- Task 10: Added teardown target to Makefile.
- Task 11: Added SESSIONS_TABLE_NAME, QUERY_USAGE_TABLE_NAME, FEEDBACK_TABLE_NAME, S3_FAISS_BUCKET to config.py with appropriate defaults. Updated .env.example.
- Task 12: CDK synth produces valid CloudFormation template with all expected resource types and outputs.

### Tests

- 11 CDK stack tests: resource counts, table schemas, Cognito config, Lambda properties, API Gateway type, CloudFront, S3 buckets, all 7 outputs
- 2 config tests: default values and env var override
- 1 existing health test: no regression

### Change Log

- 2026-04-25: Implemented Story 1.2 — full AWS infrastructure CDK stack, Dockerfile, deploy/teardown scripts, config updates. All 14 tests pass.

### File List

New files:
- backend/Dockerfile
- backend/.dockerignore
- infra/tests/__init__.py
- infra/tests/test_strengthwise_stack.py
- backend/tests/test_config.py

Modified files:
- backend/requirements.txt
- backend/config.py
- infra/stacks/strengthwise_stack.py
- scripts/deploy.sh
- scripts/teardown.sh
- Makefile
- .env.example
- _bmad-output/implementation-artifacts/sprint-status.yaml
