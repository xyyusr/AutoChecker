
import xml.etree.ElementTree as ET


def select_repaired_testcase_toxml_to_test(test_case: list, rule_testcase_xml_filepath_in_pmd_project: str, rule_testcase_xml_filepath_in_another_pmd_project: str):
    tree = ET.parse(rule_testcase_xml_filepath_in_pmd_project, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    for test_code_elem in root.findall('.//test-code'):
        problem = test_code_elem.find('description').text
        if problem not in test_case:
            root.remove(test_code_elem)
    tree.write(rule_testcase_xml_filepath_in_another_pmd_project)

def delete_fail5round_testcase_from_xml(test_case: str, rule_testcase_xml_filepath: str):
    tree = ET.parse(rule_testcase_xml_filepath, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    for test_code_elem in root.findall('.//test-code'):
        problem = test_code_elem.find('description').text
        if problem == test_case:
            root.remove(test_code_elem)

    tree.write(rule_testcase_xml_filepath)

def findCodeInTestCase(passed_testcase: list, rule_testcase_xml_filepath: str):
    xml_file_path = rule_testcase_xml_filepath
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
    xml_file_path = xml_path
    tree = ET.parse(xml_file_path, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    i = 0
    for test_code_elem in root.findall('.//test-code'):
        problem = test_code_elem.find('expected-problems').text
        if problem != "0":
            i = i + 1
            if i == id:
                code_elem = ET.ElementTree(test_code_elem)
                code_elem.write("../onecode.xml", encoding="utf-8", xml_declaration=True)

def selectOne(id: int, xml_path: str):
    xml_file_path = xml_path
    tree = ET.parse(xml_file_path, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    i = 0
    for test_code_elem in root.findall('.//test-code'):
        i = i + 1
        if i == id:
            code_elem = ET.ElementTree(test_code_elem)
            code_elem.write("../onecode.xml", encoding="utf-8", xml_declaration=True)

def countNegative(xml_path: str):
    xml_file_path = xml_path
    tree = ET.parse(xml_file_path, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    i = 0
    for test_code_elem in root.findall('.//test-code'):
        problem = test_code_elem.find('expected-problems').text
        if problem != "0":
            i = i + 1
    return i

def countTestcases(xml_path: str):
    xml_file_path = xml_path
    tree = ET.parse(xml_file_path, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    i = 0
    for test_code_elem in root.findall('.//test-code'):
        i = i + 1
    return i

def findsourccode():
    xml_file_path = "../onecode.xml"
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    code_elem = root.find('code')
    testcase = code_elem.text.strip() if code_elem is not None and code_elem.text is not None else ""
    description = root.find('description').text
    expected_problems = root.find('expected-problems').text
    testcase = testcase + "\n" + "The description of this test case is: " + description + "\n" + "The number of violating the rule in this test case is: " + expected_problems + "\n"

    return testcase

def finddescription():
    xml_file_path = "../onecode.xml"
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    description = root.find('description').text
    return description


def finderrordescription():
    xml_file_path = "../errorcode.xml"
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    description = root.find('description').text
    return description


def finderrornumber():
    xml_file_path = "../errorcode.xml"
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    num = root.find('expected-problems').text
    return num


def selecterrorcase(error: str, xml_path: str):
    error_des = ""
    if error != "":
        first_quote_index = error.find('"')
        second_quote_index = error.find('"', first_quote_index + 1)
        error_des = error[first_quote_index + 1:second_quote_index]
    xml_file_path = xml_path
    tree = ET.parse(xml_file_path, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()
    for test_code_elem in root.findall('.//test-code'):
        description = test_code_elem.find('description')
        if description.text == error_des:
            code_elem = ET.ElementTree(test_code_elem)
            code_elem.write("../errorcode.xml", encoding="utf-8", xml_declaration=True)


def finderrorsourcecode():
    xml_file_path = "../errorcode.xml"
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    code_elem = root.find('code')
    testcase = code_elem.text.strip() if code_elem is not None and code_elem.text is not None else ""
    expected_problems = root.find('expected-problems').text
    testcase = testcase + "\n" + "The number of violating the rule in this test case is: " + expected_problems + "\n"

    return testcase