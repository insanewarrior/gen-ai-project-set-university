from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    Duration,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigatewayv2 as apigwv2,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_cognito as cognito,
)
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration
from aws_cdk.aws_ecr_assets import Platform
from constructs import Construct


class StrengthwiseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- DynamoDB Tables ---

        sessions_table = dynamodb.Table(
            self,
            "SessionsTable",
            table_name="Sessions",
            partition_key=dynamodb.Attribute(
                name="userId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="sessionDate#sessionId",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        query_usage_table = dynamodb.Table(
            self,
            "QueryUsageTable",
            table_name="QueryUsage",
            partition_key=dynamodb.Attribute(
                name="userId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="date", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        feedback_table = dynamodb.Table(
            self,
            "FeedbackTable",
            table_name="Feedback",
            partition_key=dynamodb.Attribute(
                name="queryId", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # --- Cognito User Pool ---

        user_pool = cognito.UserPool(
            self,
            "UserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            custom_attributes={
                "sport": cognito.StringAttribute(mutable=True),
            },
            removal_policy=RemovalPolicy.DESTROY,
        )

        cognito.CfnUserPoolGroup(
            self,
            "PremiumGroup",
            user_pool_id=user_pool.user_pool_id,
            group_name="premium",
            description="Premium tier users with unlimited daily queries",
        )

        user_pool_client = user_pool.add_client(
            "WebClient",
            auth_flows=cognito.AuthFlow(user_srp=True),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(implicit_code_grant=True),
            ),
        )

        # --- S3 Bucket for FAISS Index ---

        faiss_bucket = s3.Bucket(
            self,
            "FaissIndexBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # --- Lambda Function (Docker Image) ---

        backend_function = lambda_.DockerImageFunction(
            self,
            "BackendFunction",
            code=lambda_.DockerImageCode.from_image_asset(
                directory="../backend",
                platform=Platform.LINUX_AMD64,
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

        sessions_table.grant_read_write_data(backend_function)
        query_usage_table.grant_read_write_data(backend_function)
        feedback_table.grant_read_write_data(backend_function)
        faiss_bucket.grant_read(backend_function)

        # --- API Gateway (HTTP API) ---

        api = apigwv2.HttpApi(
            self,
            "HttpApi",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_origins=["*"],
                allow_methods=[apigwv2.CorsHttpMethod.ANY],
                allow_headers=["*"],
            ),
        )

        integration = HttpLambdaIntegration(
            "LambdaIntegration", backend_function
        )

        api.add_routes(
            path="/{proxy+}",
            methods=[apigwv2.HttpMethod.ANY],
            integration=integration,
        )
        api.add_routes(
            path="/",
            methods=[apigwv2.HttpMethod.ANY],
            integration=integration,
        )

        # --- S3 + CloudFront for Frontend ---

        frontend_bucket = s3.Bucket(
            self,
            "FrontendBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        distribution = cloudfront.Distribution(
            self,
            "FrontendDist",
            default_behavior=cloudfront.BehaviorOptions(
                origin=(
                    origins.S3BucketOrigin
                    .with_origin_access_control(frontend_bucket)
                ),
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

        # --- CfnOutputs ---

        CfnOutput(self, "ApiUrl", value=api.url or "")
        CfnOutput(
            self,
            "CloudFrontUrl",
            value=f"https://{distribution.distribution_domain_name}",
        )
        CfnOutput(
            self,
            "FrontendBucketName",
            value=frontend_bucket.bucket_name,
        )
        CfnOutput(
            self,
            "DistributionId",
            value=distribution.distribution_id,
        )
        CfnOutput(
            self, "UserPoolId", value=user_pool.user_pool_id
        )
        CfnOutput(
            self,
            "UserPoolClientId",
            value=user_pool_client.user_pool_client_id,
        )
        CfnOutput(self, "FaissIndexBucketName", value=faiss_bucket.bucket_name)
