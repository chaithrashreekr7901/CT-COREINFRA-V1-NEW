from aws_cdk import (
    aws_s3 as s3,
    aws_kms as kms,
    Stack,
    RemovalPolicy,
    Duration,
    Tags
)
from constructs import Construct
import logging
from config.s3_config import S3_CONFIG

class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.s3_config = S3_CONFIG
        self.buckets = []
        
        if not self.s3_config['enabled']:
            return

        self.create_buckets()

    def create_buckets(self):
        """Create multiple S3 buckets with configurations"""
        count = self.s3_config.get('bucket_count', 1)  # Get count from config, default to 1
        
        for i in range(count):
            # Create unique bucket name for each instance
            bucket_name = f"{self.s3_config['name']}-{i+1}" if count > 1 else self.s3_config['name']
            
            # Create bucket with configuration
            bucket = s3.Bucket(
                self,
                f"S3Bucket-{i+1}" if count > 1 else "S3Bucket",
                bucket_name=bucket_name,
                versioned=self.s3_config['versioning'],
                encryption=self.get_encryption_config(),
                block_public_access=s3.BlockPublicAccess(
                    block_public_acls=self.s3_config['block_public_access']['block_public_acls'],
                    block_public_policy=self.s3_config['block_public_access']['block_public_policy'],
                    ignore_public_acls=self.s3_config['block_public_access']['ignore_public_acls'],
                    restrict_public_buckets=self.s3_config['block_public_access']['restrict_public_buckets']
                ),
                removal_policy=RemovalPolicy.RETAIN,
                auto_delete_objects=False
            )
            
            self.buckets.append(bucket)
            
            # Apply configurations to each bucket
            self.configure_lifecycle_rules(bucket)
            self.configure_cors(bucket)
            self.configure_logging(bucket)
            self.add_tags(bucket)

    def get_encryption_config(self):
        """Configure bucket encryption"""
        if not self.s3_config['encryption']['enabled']:
            return s3.BucketEncryption.UNENCRYPTED

        if self.s3_config['encryption']['type'] == 'KMS':
            if self.s3_config['encryption']['kms_key_id']:
                key = kms.Key.from_key_arn(
                    self,
                    'ImportedKey',
                    key_arn=self.s3_config['encryption']['kms_key_id']
                )
                return s3.BucketEncryption.KMS(key)
            return s3.BucketEncryption.KMS_MANAGED
        
        return s3.BucketEncryption.S3_MANAGED

    def configure_lifecycle_rules(self, bucket):
        """Configure bucket lifecycle rules"""
        if not self.s3_config['lifecycle_rules']:
            return

        for rule in self.s3_config['lifecycle_rules']:
            transitions = []
            for transition in rule['transitions']:
                storage_class = getattr(s3.StorageClass, transition['storage_class'])
                transitions.append(
                    s3.Transition(
                        storage_class=storage_class,
                        transition_after=Duration.days(transition['transition_after'])
                    )
                )

            bucket.add_lifecycle_rule(
                enabled=rule['enabled'],
                id=rule['id'],
                transitions=transitions,
                expiration=Duration.days(rule['expiration']['days']) if rule.get('expiration') else None
            )

    def configure_cors(self, bucket):
        """Configure CORS rules"""
        if not self.s3_config['cors']['enabled']:
            return

        cors_rules = []
        for rule in self.s3_config['cors']['rules']:
            cors_rules.append(
                s3.CorsRule(
                    allowed_methods=[getattr(s3.HttpMethods, method) for method in rule['allowed_methods']],
                    allowed_origins=rule['allowed_origins'],
                    allowed_headers=rule['allowed_headers'],
                    max_age=rule['max_age']
                )
            )

        bucket.add_cors_rule(
            allowed_methods=[s3.HttpMethods.GET],
            allowed_origins=["*"]
        )

    def configure_logging(self, bucket):
        """Configure bucket logging"""
        if not self.s3_config['logging']['enabled']:
            return

        if self.s3_config['logging']['target_bucket']:
            target_bucket = s3.Bucket.from_bucket_name(
                self,
                f'LoggingBucket-{bucket.node.id}',
                self.s3_config['logging']['target_bucket']
            )
            
            bucket.enable_logging(
                log_bucket=target_bucket,
                log_prefix=self.s3_config['logging']['target_prefix']
            )

    def add_tags(self, bucket):
        """Add tags to the bucket"""
        for key, value in self.s3_config.get('tags', {}).items():
            Tags.of(bucket).add(key, value)