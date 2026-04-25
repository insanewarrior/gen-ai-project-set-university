#!/usr/bin/env bash
set -e

ENDPOINT="${DYNAMODB_ENDPOINT:-http://localhost:8000}"
REGION="${AWS_REGION:-us-east-1}"

export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-fake}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-fake}"

create_table_if_missing() {
  local table_name="$1"
  shift
  if aws dynamodb describe-table --table-name "$table_name" --endpoint-url "$ENDPOINT" --region "$REGION" >/dev/null 2>&1; then
    echo "Table '$table_name' already exists — skipping."
  else
    echo "Creating table '$table_name'..."
    aws dynamodb create-table --table-name "$table_name" --endpoint-url "$ENDPOINT" --region "$REGION" "$@"
    echo "Table '$table_name' created."
  fi
}

# Users table
create_table_if_missing Users \
  --attribute-definitions AttributeName=userId,AttributeType=S \
  --key-schema AttributeName=userId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Sessions table
create_table_if_missing Sessions \
  --attribute-definitions AttributeName=userId,AttributeType=S AttributeName=sk,AttributeType=S \
  --key-schema AttributeName=userId,KeyType=HASH AttributeName=sk,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

echo "Seed complete."
