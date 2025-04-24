#!/usr/bin/env python3

import logging
import sys
from aws_cdk import App, Environment
from stacks.vpc_stack import VPCStack
from stacks.s3_stack import S3Stack
from config.global_config import GLOBAL_CONFIG

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    app = App()

    try:
        # Get command line arguments
        stacks_to_deploy = sys.argv[1:] if len(sys.argv) > 1 else ['all']
        
        env = Environment(
            account=GLOBAL_CONFIG['account_id'],
            region=GLOBAL_CONFIG['region']
        )

        # Create stacks based on command line arguments
        if 'all' in stacks_to_deploy or 'vpc' in stacks_to_deploy:
            logging.info("🚀 Including VPC Stack in deployment...")
            VPCStack(app, "VPCStack", env=env)
        
        if 'all' in stacks_to_deploy or 's3' in stacks_to_deploy:
            logging.info("🚀 Including S3 Stack in deployment...")
            S3Stack(app, "S3Stack", env=env)

        app.synth()
        logging.info("✅ CDK application synthesized successfully.")

    except Exception as e:
        logging.error(f"💥 Error in stack deployment: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
