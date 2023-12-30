#!/usr/bin/env python3
import os
from constructs import Construct
from aws_cdk import App, Stack
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_apigateway as _ag
from aws_cdk import aws_stepfunctions as _sfn
from aws_cdk import aws_s3 as _s3
from aws_cdk import aws_lambda as _lambda
import aws_cdk as core


class CdkStack(Stack):
    def __init__(self, scope: Construct, id: str, stack_prefix: str,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket_output = _s3.Bucket(self, "{}-bucket".format(stack_prefix),
            block_public_access=_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        function_process = _lambda.Function(
            self,
            "{}-function-process".format(stack_prefix),
            code=_lambda.AssetCode("../lambda-functions/process/"),
            handler="app.handler",
            timeout=core.Duration.seconds(60),
            tracing=_lambda.Tracing.ACTIVE,
            runtime=_lambda.Runtime.PYTHON_3_11)
        bucket_output.grant_read(function_process)
        bucket_output.grant_put(function_process)

        # IAM Roles
        sfn_role = _iam.Role(
            self,
            id='{}-sfn-role'.format(stack_prefix),
            assumed_by=_iam.ServicePrincipal('states.amazonaws.com'))

        bedrock_policy_statement = _iam.PolicyStatement(effect=_iam.Effect.ALLOW)
        bedrock_policy_statement.add_actions("bedrock:InvokeModel")
        bedrock_policy_statement.add_resources("arn:aws:bedrock:{}::foundation-model/*".format(kwargs.get("env").region))
        bedrock_policy_statement.add_resources("arn:aws:bedrock:{}:{}:provisioned-model/*".format(kwargs.get("env").region,kwargs.get("env").account))
        sfn_role.add_to_policy(bedrock_policy_statement)

        file_asl = "./app.asl.json"

        workflow = _sfn.StateMachine(self, "{}-state-machine".format(stack_prefix),
            role=sfn_role,
            state_machine_name="{}-state-machine".format(stack_prefix),
            definition_body=_sfn.DefinitionBody.from_file(file_asl),
            definition_substitutions={"s3_bucket":bucket_output.bucket_name, "lambda_arn":function_process.function_arn},
            timeout=core.Duration.minutes(5),
            comment="StepFunctions integration with bedrock: Demo-2-prompt-chaining"
        )
        function_process.grant_invoke(workflow)
        bucket_output.grant_put(workflow)

        # api = _ag.RestApi(
            # self,
            # id="{}-api-gateway".format(stack_prefix),
        # )

        # int_saveData = _ag.LambdaIntegration(fnLambda_saveData)
        # int_listData = _ag.LambdaIntegration(fnLambda_listData)
        # int_getData = _ag.LambdaIntegration(fnLambda_getData)
        # int_deleteData = _ag.LambdaIntegration(fnLambda_deleteData)

        # # URL example: api.example.com/data/
        # res_data = api.root.add_resource('data')
        # res_data.add_method('POST', int_saveData)
        # res_data.add_method('GET', int_listData)

        # # URL example: api.example.com/data/12345
        # res_data_id = res_data.add_resource('{id}')
        # res_data_id.add_method('GET', int_getData)
        # res_data_id.add_method('DELETE', int_deleteData)

        # core.CfnOutput(self,
                       # "{}-output-dynamodbTable".format(stack_prefix),
                       # value=ddb_table.table_name,
                       # export_name="{}-ddbTable".format(stack_prefix))
        # core.CfnOutput(self,
                       # "{}-output-apiEndpointURL".format(stack_prefix),
                       # value=api.url,
                       # export_name="{}-apiEndpointURL".format(stack_prefix))

env_deploy = core.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region="us-west-2")
stack_prefix = 'demo-stepfunctions-bedrock-2-prompt-chaining'
app = core.App()
stack = CdkStack(app, stack_prefix, stack_prefix=stack_prefix, env=env_deploy)
core.Tags.of(stack).add('Name', stack_prefix)

app.synth()
