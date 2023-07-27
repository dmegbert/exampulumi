import pulumi_aws as aws

from config import prefix, env, origin_header_name, origin_header_value
from resources.api_gateway import api_gw_stage


regex_pattern_set = aws.wafregional.RegexPatternSet(
    f"{prefix}-regex-pattern-set", regex_pattern_strings=[origin_header_value]
)

regex_match_set = aws.wafregional.RegexMatchSet(
    f"{prefix}-regex-match-set",
    regex_match_tuples=[
        aws.wafregional.RegexMatchSetRegexMatchTupleArgs(
            field_to_match=aws.wafregional.RegexMatchSetRegexMatchTupleFieldToMatchArgs(
                data=origin_header_name,
                type="HEADER",
            ),
            regex_pattern_set_id=regex_pattern_set.id,
            text_transformation="NONE",
        )
    ],
)

waf_rule = aws.wafregional.Rule(
    f"{prefix}-cf-waf-rule",
    metric_name=f"{env}WafMetric",
    predicates=[
        aws.wafregional.RulePredicateArgs(
            type="RegexMatch",
            data_id=regex_match_set.id,
            negated=False,
        ),
    ],
)

web_acl = aws.wafregional.WebAcl(
    f"{prefix}-web-acl",
    metric_name="apiGwMetricName",
    default_action=aws.wafregional.WebAclDefaultActionArgs(type="BLOCK"),
    rules=[
        aws.wafregional.WebAclRuleArgs(
            type="REGULAR",
            priority=1,
            rule_id=waf_rule.id,
            action=aws.wafregional.WebAclRuleActionArgs(
                type="ALLOW",
            ),
        ),
    ],
)

web_acl_association = aws.wafregional.WebAclAssociation(
    f"{prefix}-web-acl-association",
    resource_arn=api_gw_stage.arn,
    web_acl_id=web_acl.id,
)
