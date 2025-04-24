#!/usr/bin/env python3

import logging
import sys
from aws_cdk import App, Environment, Tags
from stacks.vpc_stack import VPCStack
from stacks.s3_stack import S3Stack
from config.global_config import GLOBAL_CONFIG

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    app = App()

    try:
        # Validate required configuration
        if not GLOBAL_CONFIG.get('account_id'):
            raise ValueError("AWS account ID is required in global configuration")
        if not GLOBAL_CONFIG.get('region'):
            raise ValueError("AWS region is required in global configuration")
            
        # Get command line arguments
        stacks_to_deploy = sys.argv[1:] if len(sys.argv) > 1 else ['all']
        
        env = Environment(
            account=GLOBAL_CONFIG['account_id'],
            region=GLOBAL_CONFIG['region']
        )

        # Create stacks based on command line arguments
        vpc_stack = None
        if 'all' in stacks_to_deploy or 'vpc' in stacks_to_deploy:
            logging.info("🚀 Including VPC Stack in deployment...")
            vpc_stack = VPCStack(app, "VPCStack", env=env)
        
        if 'all' in stacks_to_deploy or 's3' in stacks_to_deploy:
            logging.info("🚀 Including S3 Stack in deployment...")
            s3_stack = S3Stack(app, "S3Stack", env=env)
            if vpc_stack:
                s3_stack.add_dependency(vpc_stack)
        
        # Add common tags to all stacks
        Tags.of(app).add('Environment', GLOBAL_CONFIG.get('environment', 'development'))
        Tags.of(app).add('Project', 'aws-cloud-resource-manager')
        
        app.synth()
        logging.info("✅ CDK application synthesized successfully.")

    except Exception as e:
        logging.error(f"💥 Error in stack deployment: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
