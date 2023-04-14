import pulumi_aws as aws

from config import env, service_name, domain_name, PROD


def get_hosted_zone() -> aws.route53.Zone:
    if env == PROD:
        zone = aws.route53.Zone(
            f"{service_name}-zone",
            comment="",
            name=domain_name,
        )
        aws.route53domains.RegisteredDomain(
            f"{service_name}-registered-domain",
            domain_name=domain_name,
            name_servers=[
                aws.route53domains.RegisteredDomainNameServerArgs(
                    name=zone.name_servers[0],
                ),
                aws.route53domains.RegisteredDomainNameServerArgs(
                    name=zone.name_servers[1],
                ),
                aws.route53domains.RegisteredDomainNameServerArgs(
                    name=zone.name_servers[2],
                ),
                aws.route53domains.RegisteredDomainNameServerArgs(
                    name=zone.name_servers[3],
                ),
            ],
        )
    else:
        zone = aws.route53.get_zone(name=domain_name)
    return zone


hosted_zone = get_hosted_zone()
