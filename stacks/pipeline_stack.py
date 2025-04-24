from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_iam as iam
)
from constructs import Construct

class CICDPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create CodeBuild IAM Role
        codebuild_role = iam.Role(
            self, "CodeBuildServiceRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            description="Role for CodeBuild project"
        )

        # Add required permissions
        codebuild_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:*",
                    "cloudformation:*",
                    "iam:*",
                    "logs:*"
                ],
                resources=["*"]
            )
        )

        # Create CodeBuild Project
        codebuild.Project(
            self, "S3StackBuild",
            project_name="s3-stack-build",
            source=codebuild.Source.git_hub(
                owner="chaithrashreekr7901",
                repo="CT-COREINFRA-V1-NEW",
                branch_or_ref="chaithrashree"
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                compute_type=codebuild.ComputeType.SMALL
            ),
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
            role=codebuild_role
        )