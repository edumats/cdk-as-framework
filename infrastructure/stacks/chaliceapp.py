import os
import aws_cdk as cdk
from aws_cdk import (
    Fn,
    aws_dynamodb as dynamodb,
)
from chalice.cdk import Chalice


RUNTIME_SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), os.pardir, 'runtime')


class ChaliceApp(cdk.Stack):

    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Creates a Chalice construct
        self.chalice = Chalice(
            self, 'ChaliceApp', source_dir=RUNTIME_SOURCE_DIR,
            stage_config={
                'environment_variables': {
                    'APP_TABLE_NAME': Fn.import_value('dynamodb-table-name'),
                    'USER_POOL_ID': Fn.import_value('user-pool-arn'),
                }
            }
        )

        # Imports table from storage_infrastructure stack
        storage_stack_table = dynamodb.Table.from_table_name(
            self,
            'storage_stack_table',
            Fn.import_value('dynamodb-table-name')
        )
        # Grants Chalice to read and write data from DynamoDB table
        storage_stack_table.grant_read_write_data(
            self.chalice.get_role('DefaultRole')
        )
