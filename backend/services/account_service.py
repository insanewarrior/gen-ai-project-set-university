import boto3
from boto3.dynamodb.conditions import Attr, Key

import config


def _get_dynamodb(**kwargs):
    if config.DYNAMODB_ENDPOINT:
        kwargs.setdefault('endpoint_url', config.DYNAMODB_ENDPOINT)
        kwargs.setdefault('aws_access_key_id', 'fake')
        kwargs.setdefault('aws_secret_access_key', 'fake')
    kwargs.setdefault('region_name', 'us-east-1')
    return boto3.resource('dynamodb', **kwargs)


def delete_account(user_id: str) -> None:
    dynamodb = _get_dynamodb()

    # 1. Delete all Sessions (PK=userId, SK=sk)
    sessions_table = dynamodb.Table(config.SESSIONS_TABLE_NAME)
    response = sessions_table.query(
        KeyConditionExpression=Key('userId').eq(user_id),
        ProjectionExpression='userId, sk',
    )
    with sessions_table.batch_writer() as batch:
        for item in response['Items']:
            batch.delete_item(Key={'userId': item['userId'], 'sk': item['sk']})

    # 2. Delete all QueryUsage records (PK=userId, SK=date; 'date' is a reserved word)
    query_usage_table = dynamodb.Table(config.QUERY_USAGE_TABLE_NAME)
    response = query_usage_table.query(
        KeyConditionExpression=Key('userId').eq(user_id),
        ProjectionExpression='userId, #d',
        ExpressionAttributeNames={'#d': 'date'},
    )
    with query_usage_table.batch_writer() as batch:
        for item in response['Items']:
            batch.delete_item(Key={'userId': item['userId'], 'date': item['date']})

    # 3. Delete all Feedback (PK=queryId; no GSI on userId — full scan required)
    feedback_table = dynamodb.Table(config.FEEDBACK_TABLE_NAME)
    paginator_key = None
    while True:
        scan_kwargs = {
            'FilterExpression': Attr('userId').eq(user_id),
            'ProjectionExpression': 'queryId',
        }
        if paginator_key:
            scan_kwargs['ExclusiveStartKey'] = paginator_key
        response = feedback_table.scan(**scan_kwargs)
        with feedback_table.batch_writer() as batch:
            for item in response['Items']:
                batch.delete_item(Key={'queryId': item['queryId']})
        paginator_key = response.get('LastEvaluatedKey')
        if not paginator_key:
            break

    # 4. Delete Cognito user last — so DynamoDB is clean if this fails
    cognito = boto3.client('cognito-idp', region_name=config.COGNITO_REGION)
    cognito.admin_delete_user(
        UserPoolId=config.COGNITO_USER_POOL_ID,
        Username=user_id,
    )
