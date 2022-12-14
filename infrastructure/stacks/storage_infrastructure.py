from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_cognito as cognito,
    CfnOutput,
)
import aws_cdk as cdk


class Storage(cdk.Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Defines a Cognito User Pool
        self.authenticator = self._create_cognito_user_pool()

        # Creates a DynamoDB table
        self.dynamodb_table = self._create_ddb_table()

        # Outputs values required by other Stack
        CfnOutput(self, 'tableName',
                  value=self.dynamodb_table.table_name,
                  export_name='dynamodb-table-name')

        CfnOutput(self, 'user_pool_arn',
                  value=self.authenticator.user_pool_arn,
                  export_name='user-pool-arn')

    def _create_ddb_table(self):
        """ Returns a DynamoDB Table instance """
        # Using billing = pay_per_request for not consuming capacity
        dynamodb_table = dynamodb.Table(
            self, 'AppTable',
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=dynamodb.Attribute(
                name='PK', type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(
                name='SK', type=dynamodb.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY)
        cdk.CfnOutput(self, 'AppTableName',
                      value=dynamodb_table.table_name)
        return dynamodb_table

    def _create_cognito_user_pool(self):
        """ Retuns an instance of Cognito User Pool """
        user_pool = cognito.UserPool(
            self,
            'cdk-test-pool',
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            self_sign_up_enabled=True,
            sign_in_aliases={'email': True},
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(
                    required=True,
                    mutable=False
                ),
            ),
            user_verification=cognito.UserVerificationConfig(),
        )

        user_pool.add_client(
            'customer-app-client',
            auth_flows=cognito.AuthFlow(
                user_srp=True
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    # Client will receive tokens instead of auth code
                    implicit_code_grant=True
                ),
                # logout_uri parameter in logout endpoint must be present here
                logout_urls=['https://example.com']
            ),
        )

        # Necessary for the Cognito signup page
        user_pool.add_domain(
            'cdktest-domain',
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix='cdktest'
            ),
        )
        return user_pool
