import json

def get_rule(json_file, name):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    method_data = []

    # 遍历所有类
    for rule_info in data["ruleList"]:
        # 检查当前类是否是目标类
        if rule_info["rule_Name"] == name:
            rule_category = rule_info["rule_Package"]
            rule_name = rule_info["rule_Name"]
            rule_description = rule_info["rule_Description"]
            rule_testcase_xml_filepath = rule_info["xml_Path"]
            # 构建方法信息字典并添加到结果列表中
            method_data = {
                "rule_category": rule_category,
                "rule_name": rule_name,
                "rule_description": rule_description,
                "rule_testcase_xml_filepath": rule_testcase_xml_filepath
            }

    return method_data