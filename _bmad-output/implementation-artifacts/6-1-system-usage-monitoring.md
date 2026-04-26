# Story 6.1: System Usage Monitoring

Status: review

## Story

As an **operator**,
I want to monitor system usage via AWS CloudWatch,
So that I can track adoption, costs, and system health.

## Acceptance Criteria

1. **Given** the system is deployed and serving traffic **When** I check CloudWatch **Then** I can see Lambda invocation counts (logging endpoints vs. query endpoints), API Gateway request counts, and DynamoDB read/write capacity consumption (FR31)

2. **Given** AI coaching queries are being made **When** I check the LLM cost tracking **Then** I can see a per-query counter in DynamoDB (`QueryUsage` table) that tracks total AI queries for cost estimation (FR31)

3. **Given** the CDK stack defines the infrastructure **When** I inspect CloudWatch **Then** Lambda logs, API Gateway metrics, and DynamoDB metrics are available via the AWS Console without additional setup; the Lambda log group has a retention policy set (not indefinite)

---

## Critical Context: What Already Exists — DO NOT RECREATE

**Per-query DynamoDB counter — ALREADY IMPLEMENTED**
`rate_limit_service.check_and_increment()` in `backend/services/rate_limit_service.py` atomically increments `queryCount` in the `QueryUsage` table on every `/query` and `/analyze` call. No changes needed to the counter logic.

**`QueryUsage` table schema**: PK=`userId` (S), SK=`date` (S). Daily records have SK in `YYYY-MM-DD` format. Premium burst-control records have SK `burst:YYYY-MM-DDTHH:MM` — these must be excluded when summing total queries.

**`profile_service.get_total_query_count(user_id)`** — ALREADY EXISTS in `backend/services/profile_service.py`. Sums all `queryCount` values where SK does not start with `burst:`. No changes needed.

**CloudWatch metrics are automatic**:
- Lambda: invocation counts, error rates, duration — emitted automatically by AWS
- DynamoDB: ConsumedReadCapacityUnits, ConsumedWriteCapacityUnits — emitted automatically
- API Gateway (HTTP API): request counts, 4xx/5xx counts — emitted automatically
- Lambda stdout → CloudWatch Logs by default (no code needed)

**CDK stack is at** `infra/stacks/strengthwise_stack.py`. The `BackendFunction` Lambda is defined there. Currently, no explicit `aws_logs.LogGroup` is set → Lambda auto-creates a log group with **no retention policy** (logs accumulate indefinitely = uncapped cost). This is the main gap.

**Backend route structure** (for operator context when filtering CloudWatch Logs):
- Logging-only (no LLM, free): `/sessions`, `/exercises`, `/health`, `/me`, `/profile`, `/export`, `/account`, `/feedback`
- LLM-invoking (cost-relevant): `/query`, `/analyze`
- All routes pass through a single Lambda function; endpoint is visible in Lambda log filter patterns.

**CDK test file**: `infra/tests/test_strengthwise_stack.py`. Uses `aws_cdk.assertions.Template`. Pattern: `template.has_resource_properties("AWS::Logs::LogGroup", {...})`.

**No admin UI required** — operator accesses AWS Console directly. No frontend changes for this story.

---

## Critical Design Decisions

### Lambda Log Group — Add Explicit Resource with Retention

The only CDK change needed: add an explicit `aws_logs.LogGroup` for the Lambda function with a retention policy. Without it, Lambda auto-creates an unmanaged log group with indefinite retention.

```python
from aws_cdk import aws_logs as logs

log_group = logs.LogGroup(
    self,
    "BackendFunctionLogGroup",
    log_group_name=f"/aws/lambda/{backend_function.function_name}",
    retention=logs.RetentionDays.ONE_MONTH,
    removal_policy=RemovalPolicy.DESTROY,
)
```

Add this AFTER the `backend_function` definition (log group name depends on the function name).

Also add a `CfnOutput` for the log group name so the operator can quickly navigate:
```python
CfnOutput(self, "BackendLogGroupName", value=log_group.log_group_name)
```

### No Custom CloudWatch Dashboard

Architecture explicitly states: "No custom dashboards for MVP — AWS Console direct access." Do NOT create a `aws_cloudwatch.Dashboard` construct. The operator uses AWS Console to view Lambda, API Gateway, and DynamoDB metrics directly.

### No API Gateway Access Logging

HTTP API (v2) access logging requires a separate log group and IAM role. For MVP, API Gateway request-level metrics (count, latency, 4xx/5xx) are already available via the AWS Console under the API Gateway service without additional configuration. Do NOT add access logging to the CDK stack.

### Operator Monitoring Guide — Where to Look

The story note section describes where the operator finds each metric in AWS Console (for documentation context — no code needed):

| Metric | Console Location |
|--------|-----------------|
| Lambda invocations (total) | CloudWatch → Metrics → Lambda → `BackendFunction` → Invocations |
| Lambda errors | CloudWatch → Metrics → Lambda → `BackendFunction` → Errors |
| Lambda duration (cold start visible) | CloudWatch → Metrics → Lambda → `BackendFunction` → Duration |
| Lambda logs (per-request) | CloudWatch → Log groups → `/aws/lambda/StrengthwiseStack-BackendFunction*` |
| API Gateway request count | CloudWatch → Metrics → API Gateway → `HttpApi` → Count |
| DynamoDB reads/writes by table | CloudWatch → Metrics → DynamoDB → Per-table ConsumedReadCapacityUnits |
| Total AI queries per user | DynamoDB Console → `QueryUsage` table → Query by userId, sum queryCount where date format = YYYY-MM-DD |

---

## Tasks / Subtasks

- [x] Task 1: Update CDK stack — add explicit Lambda log group with retention
  - [x] 1.1: Add `from aws_cdk import aws_logs as logs` import to `infra/stacks/strengthwise_stack.py`
  - [x] 1.2: After `backend_function` definition, add `logs.LogGroup` construct with `log_group_name=f"/aws/lambda/{backend_function.function_name}"`, `retention=logs.RetentionDays.ONE_MONTH`, `removal_policy=RemovalPolicy.DESTROY`
  - [x] 1.3: Add `CfnOutput(self, "BackendLogGroupName", value=log_group.log_group_name)` at end of `__init__`

- [x] Task 2: Update CDK tests — verify log group with retention
  - [x] 2.1: Add `test_lambda_log_group_retention` to `infra/tests/test_strengthwise_stack.py`
    - Assert `template.resource_count_is("AWS::Logs::LogGroup", 1)` (or more if other log groups exist)
    - Assert `template.has_resource_properties("AWS::Logs::LogGroup", {"RetentionInDays": 30})`
  - [x] 2.2: Add `test_outputs_include_log_group_name` — assert `template.has_output("BackendLogGroupName", {})`
  - [x] 2.3: Run `pytest infra/tests/` to confirm all existing + new CDK tests pass

- [x] Task 3: Verify per-query counter end-to-end (no code changes, verification only)
  - [x] 3.1: Run `pytest backend/tests/test_rate_limit.py` — all pass (counter logic verified)
  - [x] 3.2: Run `pytest backend/tests/test_profile.py` — confirms `get_total_query_count` works correctly
  - [x] 3.3: Confirm `rate_limit_service.check_and_increment()` is called in BOTH `/query` and `/analyze` routers by grepping: `grep -rn "check_and_increment" backend/routers/`

- [x] Task 4: Run full regression suite
  - [x] 4.1: `pytest backend/tests/` — all existing tests pass (no backend changes = no regressions)
  - [x] 4.2: `pytest infra/tests/` — all CDK tests pass including 2 new ones

---

## Dev Notes

### CRITICAL: Log Group Name Must Reference Function Name (Not Hardcode)

CDK assigns random suffixes to function names. Always use `backend_function.function_name` in the log group name — never hardcode a string like `"StrengthwiseStack-BackendFunction"`. Using `f"/aws/lambda/{backend_function.function_name}"` ensures CDK synthesizes the correct ARN reference.

### CRITICAL: Logs.RetentionDays.ONE_MONTH = 30 Days

`aws_logs.RetentionDays.ONE_MONTH` maps to `RetentionInDays: 30` in CloudFormation. This is what the CDK assertion should check for. Do not use `RetentionDays.SIX_MONTHS` or other values — ONE_MONTH is appropriate for MVP ops costs.

### QueryUsage burst: SK exclusion

The `QueryUsage` table stores TWO kinds of items:
- **Daily counters**: SK = `YYYY-MM-DD` (e.g., `"2026-04-26"`), `queryCount` = number of LLM queries that day
- **Burst markers**: SK = `burst:YYYY-MM-DDTHH:MM`, `queryCount` = queries in this minute (premium users)

When computing total AI queries for cost estimation, only count items where SK does NOT start with `"burst:"`. This is already implemented in `profile_service.get_total_query_count()` — do not change it.

### No Backend Changes Required

All three Lambda metric types (invocations, duration, errors) and all DynamoDB metrics (ConsumedReadCapacity, SuccessfulRequestLatency) emit automatically to CloudWatch. FastAPI's exception handlers already print stack traces to stdout → CloudWatch Logs. No structured logging library (aws-lambda-powertools, etc.) needed for MVP.

### CDK Python venv is in infra/

To run CDK tests, activate the infra venv: `source infra/.venv/bin/activate && pytest infra/tests/`. The CDK module is `aws-cdk-lib`, already installed.

### Distinguishing Logging vs. AI Query Invocations in CloudWatch

Lambda invocation metrics are per-function (one function handles all routes). To distinguish logging endpoints from AI query endpoints in CloudWatch Logs:
- Use **CloudWatch Logs Insights** query: `filter @message like "/query" or @message like "/analyze"` to count AI-related invocations
- This is operator-level knowledge; no code change is required to enable it

---

### Project Structure Notes

Files to MODIFY:
```
infra/stacks/strengthwise_stack.py    ← ADD aws_logs.LogGroup + CfnOutput
infra/tests/test_strengthwise_stack.py ← ADD 2 log group tests
```

Files NOT to touch:
```
backend/services/rate_limit_service.py  ← counter already correct
backend/services/profile_service.py     ← get_total_query_count already correct
backend/routers/query.py                ← already calls check_and_increment
backend/routers/analyze.py              ← already calls check_and_increment
backend/main.py                         ← no changes
```

### References

- Architecture: `_bmad-output/planning-artifacts/architecture.md#Monitoring` — "CloudWatch (Lambda logs, API Gateway metrics, DynamoDB capacity). No custom dashboards for MVP — AWS Console direct access."
- PRD FR31: `_bmad-output/planning-artifacts/prd.md` — "The operator can monitor system usage (logging events, AI queries, active users, LLM costs) via AWS CloudWatch"
- CDK stack: `infra/stacks/strengthwise_stack.py`
- CDK tests: `infra/tests/test_strengthwise_stack.py`
- Rate limit service (counter): `backend/services/rate_limit_service.py#check_and_increment`
- Profile service (total count): `backend/services/profile_service.py#get_total_query_count`

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

CDK tests must be run from the `infra/` directory (`cd infra && source .venv/bin/activate && pytest tests/`) because the Docker image path `../backend` is resolved relative to the working directory. Running from the project root causes a "Cannot find image directory" error.

### Completion Notes List

- Added `aws_logs as logs` import to CDK stack
- Added explicit `logs.LogGroup` for BackendFunction with `RetentionDays.ONE_MONTH` (30 days) and `removal_policy=DESTROY`; log group name references `backend_function.function_name` to avoid hardcoding CDK-generated suffixes
- Added `CfnOutput("BackendLogGroupName")` for operator convenience
- Added 2 new CDK tests: `test_lambda_log_group_retention` (asserts RetentionInDays=30) and `test_outputs_include_log_group_name`
- Verified no backend code changes needed: `check_and_increment` confirmed in both `/query` and `/analyze` routers; rate_limit and profile tests all pass
- Full regression: 73 backend tests + 13 CDK tests pass (0 failures)

### File List

- `infra/stacks/strengthwise_stack.py` — added `aws_logs` import, `LogGroup` construct, `BackendLogGroupName` CfnOutput
- `infra/tests/test_strengthwise_stack.py` — added `test_lambda_log_group_retention` and `test_outputs_include_log_group_name`

### Change Log

- 2026-04-26: Added explicit Lambda log group with ONE_MONTH retention to CDK stack; added 2 CDK tests to verify retention policy and stack output
