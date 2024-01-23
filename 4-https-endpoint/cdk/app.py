#!/usr/bin/env python3
import os
from constructs import Construct
from aws_cdk import App, Stack
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_apigateway as _ag
from aws_cdk import aws_stepfunctions as _sfn
from aws_cdk import aws_events as _events
from aws_cdk import aws_events_targets as _targets
import aws_cdk.aws_secretsmanager as _secretsmanager
import aws_cdk as core


class CdkStack(Stack):
    def __init__(self, scope: Construct, id: str, stack_prefix: str,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        secret_password = _secretsmanager.Secret(self, "{}-secret".format(stack_prefix))

        connection_password = core.SecretValue.secrets_manager(
            secret_id=secret_password.secret_arn
        )

        connection = _events.Connection(
            self,
            id="{}-connection".format(stack_prefix),
            connection_name="{}-connection".format(stack_prefix),
            # connection_description="Connection for HuggingFace",
            authorization=_events.Authorization.api_key(
                "Authorization", connection_password
            ),
        )
        # endpoint="https://api-inference.huggingface.co/models/gpt2"
        endpoint = "https://api-inference.huggingface.co/models/bert-base-uncased"

        destination = _events.ApiDestination(self,
            id="{}-destination".format(stack_prefix),
            connection=connection,
            endpoint=endpoint,
            description="Integration with HuggingFace"
        )



        # IAM Roles
        sfn_role = _iam.Role(
            self,
            id='{}-sfn-role'.format(stack_prefix),
            assumed_by=_iam.ServicePrincipal('states.amazonaws.com'))

        policy_statement_secrets = _iam.PolicyStatement(effect=_iam.Effect.ALLOW)
        policy_statement_secrets.add_actions("secretsmanager:GetSecretValue")
        policy_statement_secrets.add_actions("secretsmanager:DescribeSecret")
        policy_statement_secrets.add_resources(connection.connection_secret_arn)
        sfn_role.add_to_policy(policy_statement_secrets)

        policy_statement_connection = _iam.PolicyStatement(effect=_iam.Effect.ALLOW)
        policy_statement_connection.add_actions("events:RetrieveConnectionCredentials")
        policy_statement_connection.add_resources(connection.connection_arn)
        sfn_role.add_to_policy(policy_statement_connection)


        policy_statement_invoke = _iam.PolicyStatement(effect=_iam.Effect.ALLOW)
        policy_statement_invoke.add_actions("states:InvokeHTTPEndpoint")
        # policy_statement_invoke.add_resources(workflow.state_machine_arn)
        policy_statement_invoke.add_resources("*")
        sfn_role.add_to_policy(policy_statement_invoke)

        file_asl = "./app.asl.json"

        workflow = _sfn.StateMachine(self, "{}-state-machine".format(stack_prefix),
            role=sfn_role,
            state_machine_name="{}-state-machine".format(stack_prefix),
            definition_body=_sfn.DefinitionBody.from_file(file_asl),
            definition_substitutions={"url_huggingface":endpoint,"arn_connection":connection.connection_arn},
            timeout=core.Duration.minutes(5),
            comment="StepFunctions integration with bedrock: {}".format(stack_prefix)
        )





env_deploy = core.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region="us-west-2")
stack_prefix = 'demo-stepfunctions-bedrock-4-https-endpoint'
app = core.App()
stack = CdkStack(app, stack_prefix, stack_prefix=stack_prefix, env=env_deploy)
core.Tags.of(stack).add('Name', stack_prefix)

app.synth()
