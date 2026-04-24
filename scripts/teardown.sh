#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Destroying CDK stack..."
cd "$PROJECT_ROOT/infra"
npx cdk destroy --force

echo "Teardown complete!"
