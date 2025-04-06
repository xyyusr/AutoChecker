import json

def get_rule(json_file, name):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    method_data = []
    for rule_info in data["ruleList"]:
        if rule_info["rule_Name"] == name:
            rule_category = rule_info["rule_Package"]
            rule_name = rule_info["rule_Name"]
            rule_description = rule_info["rule_Description"]
            rule_testcase_xml_filepath = rule_info["xml_Path"]
            method_data = {
                "rule_category": rule_category,
                "rule_name": rule_name,
                "rule_description": rule_description,
                "rule_testcase_xml_filepath": rule_testcase_xml_filepath
            }

    return method_data