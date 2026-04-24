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
npx cdk deploy --require-approval never --outputs-file cdk-outputs.json

# 3. Upload frontend to S3 (extract bucket name from CDK outputs)
BUCKET_NAME=$(python3 -c "
import json
data = json.load(open('cdk-outputs.json'))
print(data['StrengthwiseStack']['FrontendBucketName'])
")
echo "Uploading frontend to s3://$BUCKET_NAME..."
aws s3 sync "$PROJECT_ROOT/frontend/dist" "s3://$BUCKET_NAME" --delete

# 4. CloudFront invalidation
DIST_ID=$(python3 -c "
import json
data = json.load(open('cdk-outputs.json'))
print(data['StrengthwiseStack']['DistributionId'])
")
echo "Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
    --distribution-id "$DIST_ID" --paths "/*"

echo "Deploy complete!"
