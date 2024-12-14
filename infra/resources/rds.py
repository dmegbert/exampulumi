import pulumi_aws as aws

from config import DB_NAME, DB_USER, DB_PASSWORD, prefix
from resources.vpc import private_vpc, db_security_group

db_subnet_group = aws.rds.SubnetGroup(
    f"{prefix}-db-subnet-group",
    subnet_ids=private_vpc.private_subnet_ids,
    description=f"{prefix} subnet group for rds db",
)

db = aws.rds.Instance(
    f"{prefix}-db-instance",
    allocated_storage=20,
    backup_retention_period=15,
    engine="postgres",  # Triggers replacement
    engine_version="17.2",
    instance_class="db.t4g.micro",  # Triggers replacement
    db_name=DB_NAME,  # Triggers replacement - same db name across environments
    username=DB_USER,  # Triggers replacement
    password=DB_PASSWORD,  # Triggers replacement
    skip_final_snapshot=True,
    publicly_accessible=False,
    vpc_security_group_ids=[db_security_group.id],  # Triggers replacement
    db_subnet_group_name=db_subnet_group.name,  # Triggers replacement
)
