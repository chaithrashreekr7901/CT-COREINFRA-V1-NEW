from aws_cdk import (
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_certificatemanager as acm,
    Stack,
    Tags
)
from constructs import Construct
# Remove this line since we're not using ConfigLoader anymore
from config.vpc_config import VPC_CONFIG
import logging

class VPCStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.vpc_config = VPC_CONFIG
        # Initialize default_config before using it
        self.default_config = {
            'network_acls': {
                'enabled': True,
                'default': {
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
            }
        }
        
        if not self.vpc_config['enabled']:
            return

        self.create_vpc()
        self.create_network_acls()
        self.create_security_groups()
        self.create_vpc_peering()
        self.setup_transit_gateway()
        self.setup_client_vpn()
        self.create_vpc_endpoints()
        self.create_flow_logs()
        self.add_tags()

    def create_vpc(self):
        subnet_configurations = []
        
        # Dynamic subnet configuration based on config file
        if self.vpc_config['subnets']['public']['enabled']:
            subnet_configurations.append(
                ec2.SubnetConfiguration(
                    name=self.vpc_config['subnets']['public']['name_prefix'],
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=self.vpc_config['subnets']['public']['cidr_mask']
                )
            )

        if self.vpc_config['subnets']['private']['enabled']:
            subnet_configurations.append(
                ec2.SubnetConfiguration(
                    name=self.vpc_config['subnets']['private']['name_prefix'],
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=self.vpc_config['subnets']['private']['cidr_mask']
                )
            )

        if self.vpc_config['subnets']['isolated']['enabled']:
            subnet_configurations.append(
                ec2.SubnetConfiguration(
                    name=self.vpc_config['subnets']['isolated']['name_prefix'],
                    subnet_type=ec2.SubnetType.ISOLATED,
                    cidr_mask=self.vpc_config['subnets']['isolated']['cidr_mask']
                )
            )

        self.vpc = ec2.Vpc(
            self,
            self.vpc_config['name'],
            vpc_name=self.vpc_config['name'],
            ip_addresses=ec2.IpAddresses.cidr(self.vpc_config['cidr']),
            max_azs=self.vpc_config['availability_zones'],
            enable_dns_hostnames=self.vpc_config['dns_options']['enable_dns_hostnames'],
            enable_dns_support=self.vpc_config['dns_options']['enable_dns_support'],
            nat_gateways=self.vpc_config['nat_gateways']['count'] 
                if self.vpc_config['nat_gateways']['enabled'] else 0,
            subnet_configuration=subnet_configurations
        )

        # Enhanced network_acls default configuration
        self.default_config['network_acls'] = {
            'enabled': True,
            'default': {
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
        }

    def create_network_acls(self):
        if not self.vpc_config['network_acls']['enabled']:
            return

        # Ensure network_acls is properly structured
        if not isinstance(self.vpc_config['network_acls'], dict):
            self.vpc_config['network_acls'] = self.default_config['network_acls']

        for nacl_name, nacl_config in self.vpc_config['network_acls'].items():
            if nacl_name == 'default':
                continue

            # Check if nacl_config is a dictionary and contains 'inbound_rules'
            if not isinstance(nacl_config, dict) or 'inbound_rules' not in nacl_config:
                logging.error(f"Invalid NACL configuration for {nacl_name}")
                continue

            network_acl = ec2.NetworkAcl(
                self,
                f"{self.vpc_config['name']}-{nacl_name}-nacl",
                vpc=self.vpc,
                subnet_selection=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PUBLIC
                )
            )

            for rule in nacl_config['inbound_rules']:
                network_acl.add_entry(
                    id=f"inbound-{rule['rule_number']}",
                    cidr=ec2.AclCidr.ipv4(rule['cidr_block']),
                    rule_number=rule['rule_number'],
                    traffic=ec2.AclTraffic.all_traffic(),
                    direction=ec2.TrafficDirection.INGRESS,
                    rule_action=ec2.Action.ALLOW if rule['rule_action'].upper() == 'ALLOW' else ec2.Action.DENY
                )

    def create_security_groups(self):
        if not self.vpc_config['security_groups']['enabled']:
            return

        # Ensure security_groups is a dictionary
        if not isinstance(self.vpc_config['security_groups'], dict):
            logging.error("Invalid security groups configuration")
            return

        for sg_name, sg_config in self.vpc_config['security_groups'].items():
            if sg_name in ['default', 'enabled']:
                continue

            # Ensure sg_config is a dictionary
            if not isinstance(sg_config, dict):
                logging.error(f"Invalid security group configuration for {sg_name}")
                continue

            security_group = ec2.SecurityGroup(
                self,
                f"{self.vpc_config['name']}-{sg_name}-sg",
                vpc=self.vpc,
                description=sg_config['description'],
                allow_all_outbound=False
            )

            for rule in sg_config.get('ingress_rules', []):
                security_group.add_ingress_rule(
                    peer=ec2.Peer.ipv4(rule['cidr_blocks'][0]),
                    connection=ec2.Port.tcp(rule['from_port']),
                    description=rule['description']
                )

    def create_vpc_peering(self):
        if not self.vpc_config['vpc_peering']['enabled']:
            return

        for connection in self.vpc_config['vpc_peering']['connections']:
            ec2.CfnVPCPeeringConnection(
                self,
                f"{self.vpc_config['name']}-peer-{connection['peer_vpc_id']}",
                vpc_id=self.vpc.vpc_id,
                peer_vpc_id=connection['peer_vpc_id'],
                peer_region=connection.get('peer_region'),
                peer_owner_id=connection.get('peer_owner_id')
            )

    def setup_transit_gateway(self):
        if not self.vpc_config['transit_gateway']['enabled']:
            return

        ec2.CfnTransitGatewayAttachment(
            self,
            f"{self.vpc_config['name']}-tgw-attachment",
            transit_gateway_id=self.vpc_config['transit_gateway']['id'],
            vpc_id=self.vpc.vpc_id,
            subnet_ids=self.vpc_config['transit_gateway']['subnets']
        )

    def setup_client_vpn(self):
        if not self.vpc_config['client_vpn']['enabled']:
            return

        ec2.CfnClientVpnEndpoint(
            self,
            f"{self.vpc_config['name']}-client-vpn",
            client_cidr_block=self.vpc_config['client_vpn']['client_cidr'],
            server_certificate_arn=self.vpc_config['client_vpn']['server_certificate_arn'],
            authentication_options=[{
                'type': 'certificate-authentication',
                'mutualAuthentication': {
                    'clientRootCertificateChainArn': 
                        self.vpc_config['client_vpn']['server_certificate_arn']
                }
            }],
            vpc_id=self.vpc.vpc_id
        )

    def create_vpc_endpoints(self):
        if not self.vpc_config['vpc_endpoints']['enabled']:
            return

        for endpoint_name, endpoint_config in self.vpc_config['vpc_endpoints']['endpoints'].items():
            if not endpoint_config['enabled']:
                continue

            if endpoint_config['type'] == 'Gateway':
                self.vpc.add_gateway_endpoint(
                    endpoint_name,
                    service=ec2.GatewayVpcEndpointAwsService(endpoint_config['service'])
                )
            elif endpoint_config['type'] == 'Interface':
                self.vpc.add_interface_endpoint(
                    endpoint_name,
                    service=ec2.InterfaceVpcEndpointService(
                        name=endpoint_config['service'],
                        port=443
                    ),
                    private_dns_enabled=endpoint_config.get('private_dns_enabled', True)
                )

    def create_flow_logs(self):
        if not self.vpc_config['flow_logs']['enabled']:
            return

        log_group = logs.LogGroup(
            self,
            f"{self.vpc_config['name']}-flow-logs",
            retention=logs.RetentionDays(
                self.vpc_config['flow_logs']['retention_days']
            )
        )

        ec2.FlowLog(
            self,
            f"{self.vpc_config['name']}-flow-log",
            resource_type=ec2.FlowLogResourceType.from_vpc(self.vpc),
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(log_group),
            traffic_type=ec2.FlowLogTrafficType[
                self.vpc_config['flow_logs']['traffic_type']
            ]
        )

    def add_tags(self):
        for key, value in self.vpc_config.get('tags', {}).items():
            Tags.of(self.vpc).add(key, value)