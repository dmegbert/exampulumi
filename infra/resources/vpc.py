import pulumi_aws as aws
import pulumi_awsx as awsx

from config import prefix

default_vpc = awsx.ec2.DefaultVpc("default-vpc")

private_vpc = awsx.ec2.Vpc(
    "vpc",
    awsx.ec2.VpcArgs(
        nat_gateways=awsx.ec2.NatGatewayConfigurationArgs(
            strategy=awsx.ec2.NatGatewayStrategy.SINGLE,
        ),
    ),
)

db_security_group = aws.ec2.SecurityGroup(
    f"{prefix}-db-private-security-group",
    vpc_id=private_vpc.vpc_id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=5432,
            to_port=5432,
            cidr_blocks=["10.0.0.0/16"],
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
)

# ec_2_bastion_security_group = aws.ec2.SecurityGroup(
#     f"{env}-ec_2_bastion_security_group",
#     description=f"Security group for ec2 bastion in {env}",
#     ingress=[
#         aws.ec2.SecurityGroupIngressArgs(
#             description="ssh allowed",
#             from_port=22,
#             protocol="tcp",
#             to_port=22,
#             cidr_blocks=["0.0.0.0/0"],
#         )
#     ],
#     egress=[
#         aws.ec2.SecurityGroupEgressArgs(
#             description="ssh allowed",
#             from_port=22,
#             protocol="tcp",
#             to_port=22,
#             cidr_blocks=["0.0.0.0/0"],
#         )
#     ],
#     vpc_id=private_vpc.vpc_id,
# )
