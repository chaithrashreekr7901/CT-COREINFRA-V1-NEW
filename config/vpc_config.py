# VPC Configuration Settings

# Basic VPC Settings
VPC_NAME = "my-vpc"
VPC_CIDR = "10.0.0.0/16"
VPC_ENABLED = True
AVAILABILITY_ZONES = 2

# DNS Settings
DNS_HOSTNAMES_ENABLED = True
DNS_SUPPORT_ENABLED = True

# Subnet Configuration
SUBNET_CONFIGURATION = {
    'public': {
        'enabled': True,
        'count': 2,
        'cidr_mask': 24,
        'name_prefix': 'Public'
    },
    'private': {
        'enabled': True,
        'count': 2,
        'cidr_mask': 24,
        'name_prefix': 'Private'
    },
    'isolated': {
        'enabled': False,
        'count': 0,
        'cidr_mask': 24,
        'name_prefix': 'Isolated'
    }
}

# Network Components
NAT_GATEWAYS_ENABLED = True
NAT_GATEWAYS_COUNT = 1
INTERNET_GATEWAY_ENABLED = True

# Network ACLs
NETWORK_ACLS_ENABLED = False
DEFAULT_NETWORK_ACLS = {
    'inbound_rules': [
        {
            'rule_number': 100,
            'protocol': -1,
            'rule_action': 'allow',
            'cidr_block': '0.0.0.0/0'
        }
    ],
    'outbound_rules': [
        {
            'rule_number': 100,
            'protocol': -1,
            'rule_action': 'allow',
            'cidr_block': '0.0.0.0/0'
        }
    ]
}

# Security Groups
SECURITY_GROUPS_ENABLED = True
DEFAULT_SECURITY_GROUP = {
    'description': 'Default security group',
    'ingress_rules': [
        {
            'description': 'Allow HTTPS',
            'from_port': 443,
            'to_port': 443,
            'protocol': 'tcp',
            'cidr_blocks': ['0.0.0.0/0']
        }
    ],
    'egress_rules': [
        {
            'description': 'Allow all outbound',
            'from_port': -1,
            'to_port': -1,
            'protocol': '-1',
            'cidr_blocks': ['0.0.0.0/0']
        }
    ]
}

# VPC Peering
VPC_PEERING_ENABLED = False
VPC_PEERING_CONNECTIONS = [
    {
        'peer_vpc_id': 'vpc-xxxxx',
        'peer_region': 'us-east-1',
        'peer_owner_id': '123456789012'
    }
]

# Transit Gateway
TRANSIT_GATEWAY_ENABLED = False
TRANSIT_GATEWAY_ID = 'tgw-xxxxx'
TRANSIT_GATEWAY_SUBNETS = ['subnet-xxxxx1', 'subnet-xxxxx2']

# Client VPN
CLIENT_VPN_ENABLED = False
CLIENT_VPN_CIDR = '172.16.0.0/22'
CLIENT_VPN_CERT_ARN = 'arn:aws:acm:region:account:certificate/xxxxx'
CLIENT_VPN_TARGET_SUBNETS = ['subnet-xxxxx1']

# VPC Endpoints
VPC_ENDPOINTS_ENABLED = False
VPC_ENDPOINTS = {
    's3': {
        'enabled': True,
        'service': 's3',
        'type': 'Gateway'
    },
    'dynamodb': {
        'enabled': False,
        'service': 'dynamodb',
        'type': 'Gateway'
    },
    'ssm': {
        'enabled': False,
        'service': 'ssm',
        'type': 'Interface',
        'private_dns_enabled': True
    }
}

# Flow Logs
FLOW_LOGS_ENABLED = False
FLOW_LOGS_DESTINATION_TYPE = 'cloudwatch'
FLOW_LOGS_RETENTION_DAYS = 7
FLOW_LOGS_TRAFFIC_TYPE = 'ALL'

# Resource Tags
VPC_TAGS = {
    'Environment': 'dev',
    'Project': 'my-project'
}

# You can also create a consolidated dictionary for easier import
VPC_CONFIG = {
    'name': VPC_NAME,
    'cidr': VPC_CIDR,
    'enabled': VPC_ENABLED,
    'availability_zones': AVAILABILITY_ZONES,
    'dns_options': {
        'enable_dns_hostnames': DNS_HOSTNAMES_ENABLED,
        'enable_dns_support': DNS_SUPPORT_ENABLED
    },
    'subnets': {
        'enabled': True,
        'public': SUBNET_CONFIGURATION['public'],
        'private': SUBNET_CONFIGURATION['private'],
        'isolated': SUBNET_CONFIGURATION['isolated']
    },
    'nat_gateways': {
        'enabled': NAT_GATEWAYS_ENABLED,
        'count': NAT_GATEWAYS_COUNT
    },
    'internet_gateway': {
        'enabled': INTERNET_GATEWAY_ENABLED
    },
    'network_acls': {
        'enabled': NETWORK_ACLS_ENABLED,
        'default': DEFAULT_NETWORK_ACLS
    },
    'security_groups': {
        'enabled': SECURITY_GROUPS_ENABLED,
        'default': DEFAULT_SECURITY_GROUP
    },
    'vpc_peering': {
        'enabled': VPC_PEERING_ENABLED,
        'connections': VPC_PEERING_CONNECTIONS
    },
    'transit_gateway': {
        'enabled': TRANSIT_GATEWAY_ENABLED,
        'id': TRANSIT_GATEWAY_ID,
        'subnets': TRANSIT_GATEWAY_SUBNETS
    },
    'client_vpn': {
        'enabled': CLIENT_VPN_ENABLED,
        'client_cidr': CLIENT_VPN_CIDR,
        'server_certificate_arn': CLIENT_VPN_CERT_ARN,
        'target_subnets': CLIENT_VPN_TARGET_SUBNETS
    },
    'vpc_endpoints': {
        'enabled': VPC_ENDPOINTS_ENABLED,
        'endpoints': VPC_ENDPOINTS
    },
    'flow_logs': {
        'enabled': FLOW_LOGS_ENABLED,
        'destination_type': FLOW_LOGS_DESTINATION_TYPE,
        'retention_days': FLOW_LOGS_RETENTION_DAYS,
        'traffic_type': FLOW_LOGS_TRAFFIC_TYPE
    },
    'tags': VPC_TAGS
}