from aws_cdk import Stack
from constructs import Construct


class StrengthwiseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TODO: DynamoDB tables (Story 1.2)
        # TODO: Lambda function + API Gateway (Story 1.2)
        # TODO: S3 bucket for frontend hosting (Story 1.2)
        # TODO: CloudFront distribution (Story 1.2)
        # TODO: Cognito user pool (Story 1.3)
