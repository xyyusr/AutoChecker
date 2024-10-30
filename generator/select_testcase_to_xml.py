
import xml.etree.ElementTree as ET

from generator.cmd_utils import jar_run


def select_repaired_testcase_toxml_to_test(test_case: list, rule_testcase_xml_filepath: str):
    # XML文件路径
    xml_file_path = rule_testcase_xml_filepath[
                    :26] + "pmd-pmd_releases-7.0.0-rc4-testsingle/" + rule_testcase_xml_filepath[26:]

    # 解析XML文件
    tree = ET.parse(rule_testcase_xml_filepath, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()

    for test_code_elem in root.findall('.//test-code'):
        problem = test_code_elem.find('description').text
        if problem not in test_case:
            root.remove(test_code_elem)

    # 将修改后的XML写回文件
    tree.write(xml_file_path)

def delete_fail5round_testcase_from_xml(test_case: str, rule_testcase_xml_filepath: str):

    # 解析XML文件
    tree = ET.parse(rule_testcase_xml_filepath, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()

    for test_code_elem in root.findall('.//test-code'):
        problem = test_code_elem.find('description').text
        if problem == test_case:
            root.remove(test_code_elem)

    # 将修改后的XML写回文件
    tree.write(rule_testcase_xml_filepath)

def findCodeInTestCase(passed_testcase: list, rule_testcase_xml_filepath: str):
    # XML文件路径
    xml_file_path = rule_testcase_xml_filepath[
                    :26] + "pmd-pmd_releases-7.0.0-rc4-testsingle/" + rule_testcase_xml_filepath[26:]

    # 解析XML文件
    tree = ET.parse(xml_file_path, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    passed_testcase_code = ""
    for test_code_elem in root.findall('.//test-code'):
        problem = test_code_elem.find('description').text
        problem_num = int(test_code_elem.find('expected-problems').text)
        if problem in passed_testcase:
            code = test_code_elem.find('code').text.strip()
            if code.startswith("//"):
                index = code.find("\n")
                code = code[index+1:]
            if problem_num > 0:
                passed_testcase_code = passed_testcase_code + "This checker has passed this negative testcase:\n" + code + "\n"
            else:
                passed_testcase_code = passed_testcase_code + "This checker has passed this positive testcase:\n" + code + "\n"
    return passed_testcase_code


def select(id: int, xml_path: str):
    # XML文件路径
    xml_file_path = xml_path

    # 解析XML文件
    tree = ET.parse(xml_file_path, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    i = 0

    for test_code_elem in root.findall('.//test-code'):
        problem = test_code_elem.find('expected-problems').text
        if problem != "0":
            i = i + 1
            if i == id:
                # 创建一个新的XML文件
                code_elem = ET.ElementTree(test_code_elem)
                code_elem.write("../testcase/onecode.xml", encoding="utf-8", xml_declaration=True)

def selectOne(id: int, xml_path: str):
    # XML文件路径
    xml_file_path = xml_path

    # 解析XML文件
    tree = ET.parse(xml_file_path, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    i = 0

    for test_code_elem in root.findall('.//test-code'):
        i = i + 1
        if i == id:
            # 创建一个新的XML文件
            code_elem = ET.ElementTree(test_code_elem)
            code_elem.write("../testcase/onecode.xml", encoding="utf-8", xml_declaration=True)

def countNegative(xml_path: str):
    # XML文件路径
    xml_file_path = xml_path

    # 解析XML文件
    tree = ET.parse(xml_file_path, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    i = 0

    for test_code_elem in root.findall('.//test-code'):
        problem = test_code_elem.find('expected-problems').text
        if problem != "0":
            i = i + 1
    return i

def countTestcases(xml_path: str):
    # XML文件路径
    xml_file_path = xml_path

    # 解析XML文件
    tree = ET.parse(xml_file_path, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    i = 0

    for test_code_elem in root.findall('.//test-code'):
        i = i + 1
    return i

def findsourccode():
    # XML文件路径
    xml_file_path = "../testcase/onecode.xml"

    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # 获取 <code> 元素
    code_elem = root.find('code')
    # 获取 Java 代码内容
    testcase = code_elem.text.strip() if code_elem is not None and code_elem.text is not None else ""
    description = root.find('description').text
    expected_problems = root.find('expected-problems').text
    testcase = testcase + "\n" + "The description of this test case is: " + description + "\n" + "The number of violating the rule in this test case is: " + expected_problems + "\n"

    return testcase

def findonesourccode(test_case_ast : str):
    # XML文件路径
    xml_file_path = "../testcase/onecode.xml"

    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # 获取 <code> 元素
    code_elem = root.find('code')
    # 获取 Java 代码内容
    testcase = code_elem.text.strip() if code_elem is not None and code_elem.text is not None else ""
    description = root.find('description').text
    expected_problems = root.find('expected-problems').text

    if expected_problems == "0":
        testcase = ". This is a positive test case" + "\n```java\n" + testcase + "\n```\n" + "Its abstract syntax tree is:\n" + test_case_ast + "\n"
    else:
        testcase = ". This is a negative test case" + "\n```java\n" + testcase + "\n```\n" + "Its abstract syntax tree is:\n" + test_case_ast + "\n"

    return testcase

def finddescription():
    # XML文件路径
    xml_file_path = "../testcase/onecode.xml"

    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    description = root.find('description').text

    return description


def finderrordescription():
    # XML文件路径
    xml_file_path = "../testcase/errorcode.xml"

    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    description = root.find('description').text

    return description


def finderrornumber():
    # XML文件路径
    xml_file_path = "../testcase/errorcode.xml"

    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    num = root.find('expected-problems').text

    return num


def selecterrorcase(error: str, xml_path: str):
    error_des = ""

    if error != "":
        # 找到第一个引号的索引
        first_quote_index = error.find('"')
        # 找到第二个引号的索引，从第一个引号之后开始搜索
        second_quote_index = error.find('"', first_quote_index + 1)
        # 提取两个引号之间的子字符串
        error_des = error[first_quote_index + 1:second_quote_index]


    # XML文件路径
    xml_file_path = xml_path
    # 解析XML文件
    tree = ET.parse(xml_file_path, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    for test_code_elem in root.findall('.//test-code'):
        description = test_code_elem.find('description')
        if description.text == error_des:
            # 创建一个新的XML文件
            code_elem = ET.ElementTree(test_code_elem)
            code_elem.write("../testcase/errorcode.xml", encoding="utf-8", xml_declaration=True)


def finderrorsourcecode():
    # XML文件路径
    xml_file_path = "../testcase/errorcode.xml"

    # 解析XML文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # 获取 <code> 元素
    code_elem = root.find('code')
    # 获取 Java 代码内容
    testcase = code_elem.text.strip() if code_elem is not None and code_elem.text is not None else ""
    expected_problems = root.find('expected-problems').text
    testcase = testcase + "\n" + "The number of violating the rule in this test case is: " + expected_problems + "\n"

    return testcase

# select(1, "D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4/pmd-java/src/test/resources/net/sourceforge/pmd/lang/java/rule/design/xml/SingularField.xml")
# print(findsourccode())

# selecterrorcase(
#     ['error_rules_info: failed test cases','error_rules_info: "appending single char, should be ok" resulted in wrong number of failures, ==> expected: <1> but was: <0>','error_rules_info: "appending single character string, should fail" resulted in wrong number of failures, ==> expected: <0> but was: <1>'],
#     "/Users/xyy/Desktop/PMD/pmd-pmd_releases-7.0.0-rc4/pmd-java/src/test/resources/net/sourceforge/pmd/lang/java/rule/performance/xml/AppendCharacterWithChar.xml"
# )
# print(finderrorsourcecode())
# ERROR_AST_command = os.path.join("/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home/bin",
#                                  "java -jar CodeToAST.jar /Users/xyy/PycharmProjects/ChatRuleGen/testcase/errorcode.xml /Users/xyy/PycharmProjects/ChatRuleGen/testcase/errorast.txt")
# jar_run([ERROR_AST_command], "/Users/xyy/PycharmProjects/ChatRuleGen")
# delete_fail5round_testcase_from_xml("appending single character string, should fail", "D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4/pmd-java/src/test/resources/net/sourceforge/pmd/lang/java/rule/performance/xml/AppendCharacterWithChar.xml")
# print(findsourccode())