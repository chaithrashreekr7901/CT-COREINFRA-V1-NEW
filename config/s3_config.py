# S3 Bucket Configuration Settings

# Basic Bucket Settings
BUCKET_NAME = "new-buckethgefhdjkhd"
BUCKET_ENABLED = True
BUCKET_COUNT = 1  # Default value for number of buckets to create

# Versioning Configuration
VERSIONING_ENABLED = True

# Encryption Configuration
ENCRYPTION = {
    "enabled": True,
    "type": "KMS",  # Options: KMS, S3_MANAGED
    "kms_key_id": None  # Optional: Specify KMS key ID if using KMS
}

# Lifecycle Rules
# Update the storage class to match the actual enum value
LIFECYCLE_RULES = [
    {
        "enabled": True,
        "id": "move-to-ia",
        "transitions": [
            {
                "storage_class": "INTELLIGENT_TIERING",  # This must match the enum value in aws_cdk.aws_s3.StorageClass
                "transition_after": 90
            }
        ],
        "expiration": {
            "days": 365
        }
    }
]

# Public Access Block Configuration
BLOCK_PUBLIC_ACCESS = {
    "block_public_acls": True,
    "block_public_policy": True,
    "ignore_public_acls": True,
    "restrict_public_buckets": True
}

# CORS Configuration
CORS_ENABLED = False
CORS_RULES = [
    {
        "allowed_methods": ["GET"],
        "allowed_origins": ["*"],
        "allowed_headers": ["*"],
        "max_age": 3000
    }
]

# Logging Configuration
LOGGING = {
    "enabled": False,
    "target_bucket": None,
    "target_prefix": "logs/"
}

# Tags
BUCKET_TAGS = {
    "Environment": "Development",
    "Project": "CloudResourceManager",
    "ManagedBy": "CDK"
}

# Create a consolidated dictionary for easier import
S3_CONFIG = {
    "name": BUCKET_NAME,
    "enabled": BUCKET_ENABLED,
    "bucket_count": BUCKET_COUNT,  # Add bucket count to config
    "versioning": VERSIONING_ENABLED,
    "encryption": ENCRYPTION,
    "lifecycle_rules": LIFECYCLE_RULES,
    "block_public_access": BLOCK_PUBLIC_ACCESS,
    "cors": {
        "enabled": CORS_ENABLED,
        "rules": CORS_RULES
    },
    "logging": LOGGING,
    "tags": BUCKET_TAGS
}