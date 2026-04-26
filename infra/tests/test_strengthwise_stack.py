import aws_cdk as cdk
from aws_cdk.assertions import Template

from stacks.strengthwise_stack import StrengthwiseStack


def _template() -> Template:
    app = cdk.App()
    stack = StrengthwiseStack(app, "TestStack")
    return Template.from_stack(stack)


def test_dynamodb_tables_created():
    template = _template()
    template.resource_count_is("AWS::DynamoDB::Table", 3)


def test_sessions_table_schema():
    template = _template()
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "TableName": "Sessions",
            "KeySchema": [
                {
                    "AttributeName": "userId",
                    "KeyType": "HASH",
                },
                {
                    "AttributeName": "sessionDate#sessionId",
                    "KeyType": "RANGE",
                },
            ],
            "BillingMode": "PAY_PER_REQUEST",
        },
    )


def test_query_usage_table_schema():
    template = _template()
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "TableName": "QueryUsage",
            "KeySchema": [
                {
                    "AttributeName": "userId",
                    "KeyType": "HASH",
                },
                {
                    "AttributeName": "date",
                    "KeyType": "RANGE",
                },
            ],
            "BillingMode": "PAY_PER_REQUEST",
        },
    )


def test_feedback_table_schema():
    template = _template()
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "TableName": "Feedback",
            "KeySchema": [
                {
                    "AttributeName": "queryId",
                    "KeyType": "HASH",
                },
            ],
            "BillingMode": "PAY_PER_REQUEST",
        },
    )


def test_cognito_user_pool():
    template = _template()
    template.resource_count_is("AWS::Cognito::UserPool", 1)
    template.has_resource_properties(
        "AWS::Cognito::UserPool",
        {
            "AutoVerifiedAttributes": ["email"],
        },
    )


def test_cognito_client():
    template = _template()
    template.resource_count_is(
        "AWS::Cognito::UserPoolClient", 1
    )
    template.has_resource_properties(
        "AWS::Cognito::UserPoolClient",
        {
            "ExplicitAuthFlows": [
                "ALLOW_USER_SRP_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
            ],
        },
    )


def test_lambda_function():
    template = _template()
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "MemorySize": 512,
            "Timeout": 30,
            "PackageType": "Image",
        },
    )


def test_api_gateway_http_api():
    template = _template()
    template.resource_count_is("AWS::ApiGatewayV2::Api", 1)
    template.has_resource_properties(
        "AWS::ApiGatewayV2::Api",
        {"ProtocolType": "HTTP"},
    )


def test_cloudfront_distribution():
    template = _template()
    template.resource_count_is(
        "AWS::CloudFront::Distribution", 1
    )


def test_s3_buckets():
    template = _template()
    template.resource_count_is("AWS::S3::Bucket", 2)


def test_outputs_present():
    template = _template()
    template.has_output("ApiUrl", {})
    template.has_output("CloudFrontUrl", {})
    template.has_output("FrontendBucketName", {})
    template.has_output("DistributionId", {})
    template.has_output("UserPoolId", {})
    template.has_output("UserPoolClientId", {})
    template.has_output("FaissIndexBucketName", {})


def test_lambda_log_group_retention():
    template = _template()
    template.has_resource_properties(
        "AWS::Logs::LogGroup",
        {"RetentionInDays": 30},
    )


def test_outputs_include_log_group_name():
    template = _template()
    template.has_output("BackendLogGroupName", {})
