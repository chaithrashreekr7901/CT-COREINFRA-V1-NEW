import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_cloud_resource_manager.aws_cloud_resource_manager_stack import AwsCloudResourceManagerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_cloud_resource_manager/aws_cloud_resource_manager_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsCloudResourceManagerStack(app, "aws-cloud-resource-manager")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
