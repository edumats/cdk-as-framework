import os
import boto3
from chalice import Chalice, CognitoUserPoolAuthorizer


app = Chalice(app_name='cdkdemo')
dynamodb = boto3.resource('dynamodb')
dynamodb_table = dynamodb.Table(os.environ.get('APP_TABLE_NAME'))

# Creates an API Gateway Authorizer
authorizer = CognitoUserPoolAuthorizer(
    'cdk-test-pool',  # Name of authorizer
    [os.environ.get('USER_POOL_ID')] # Gets User Pool ARN
)


@app.route('/users', methods=['POST'], authorizer=authorizer)
def create_user():
    """ Creates a user in DynamoDB Table """
    # Gets json payload in request body
    request = app.current_request.json_body

    # Creates an item
    item = {
        'PK': f'User#{request["username"]}',
        'SK': f'Profile#{request["username"]}',
    }

    # Item is created or updated in database
    dynamodb_table.put_item(Item=item)

    # Return empty dictionary
    return {}


@app.route('/users/{username}', methods=['GET'])
def get_user(username):
    """ Gets a user from DynamoDB Table """
    # Creates a key to search for
    key = {
        'PK': f'User#{username}',
        'SK': 'Profile#{username}',
    }

    # Gets key from db
    item = dynamodb_table.get_item(Key=key)['Item']

    return item


@app.route('/users', methods=['GET'], authorizer=authorizer)
def get_users():
    return {'hello': 'world'}
