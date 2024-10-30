import tiktoken
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from generator.cmd_utils import jar_run
from generator.getRule import get_rule
from generator.parseranswer import parse_java_code_from_answer
from generator.parsererror import MavenOutputParser
from generator.select_testcase_to_xml import countTestcases, countNegative
from generator.testrule import TestChecker

class CheckerGenerator(object):
    def __init__(self, openai_api_key: str, model_name: str) -> None:
        self.model_name = model_name
        self.openai_key = openai_api_key
        self.client = ChatOpenAI(model=self.model_name, api_key=self.openai_key, base_url="https://api2.aigcbest.top/v1")
        self.encoding = tiktoken.encoding_for_model("gpt-4-0613")
        self.input_num_tokens = 0
        self.output_num_tokens = 0

        self.repair_code_snippet_prompt = PromptTemplate(
            input_variables=["code", "code_snippet"],
            template=
            """You are an expert in writing java rule checkers in PMD tool version 7.0.0.
Here is a checker code for a rule:
Check code:
```
{code}
```

This code use some of these code snippets:
{code_snippet}

If code snippet above is used in checker, please confirm that the parameter type is passes correctly and the code snippet body is not changed, if changed, replace with original code snippet.

Note, keep checker's original logic.
Finally, return complete checker code to me.
            """
        )
        self.checker_prompt = PromptTemplate(
            input_variables=["Rule_description","rule_package","rule_name"],
            template=
            """You are an expert in writing java rule checkers and I need your help to generate a custom java rule checker in PMD tool version 7.0.0. 
I will give you the rule description, please give me the complete checker code of the rule including the import info, do not contain pseudocode, and do not give it step by step. No comment needed.

Rule description: {Rule_description};

The checker code framework(you must conform to):
```java
package {rule_package};
import net.sourceforge.pmd.lang.java.rule.AbstractJavaRulechainRule;
import net.sourceforge.pmd.lang.java.ast.*;
import net.sourceforge.pmd.lang.java.ast.internal.*;
import net.sourceforge.pmd.lang.java.types.*;
import net.sourceforge.pmd.lang.java.symbols.*;
import net.sourceforge.pmd.lang.java.ast.JavaNode;
import net.sourceforge.pmd.lang.ast.NodeStream;
import java.util.*;
import java.lang.*;

{rule_name} {{
    public rule_name() {{
        super(node1_Of_AST_to_visit.class, node2_Of_AST_to_visit.class, ...);
    }}
    @Override
    public Object visit(node1_Of_AST_to_visit node, Object data) {{
        return super.visit(node, data);
    }}
    @Override
    public Object visit(node2_Of_AST_to_visit node, Object data) {{
        return super.visit(node, data);
    }}
    ...
}}
```
Some useful packages are already imported, if you need other packages, please import additionally.
"""
        )

        self.repair_compile_error_prompt = PromptTemplate(
            input_variables=["Rule_description", "source_code", "failed_info"],
            template=
            """You are an expert in writing java rule checkers in PMD tool version 7.0.0. 
Here is a checker for this rule:
Rule description: {Rule_description};
And the source code of the checker is as follows:
```
{source_code}
```
This checker is compiled failed, and the failure info is:
{failed_info}

Please help me repair this checker and give me repaired complete checker code.
You should keep code that is unrelated to failure info unchanged. 
"""
        )

        self.global_rule_name = ""

    def run_llm(self, query):
        self.input_num_tokens = self.input_num_tokens + len(self.encoding.encode(query))
        answer = self.client.invoke(query).content
        self.output_num_tokens = self.output_num_tokens + len(self.encoding.encode(answer))
        return answer

    def class_is_correctly_imported(self, checker: str, ast_classes: list):
        new_checker = ""
        content = [line for line in checker.split("\n")]
        for line in content:
            if not line.startswith("import net"):
                if(line.startswith("public class")):
                    new_checker += "import net.sourceforge.pmd.lang.java.rule.AbstractJavaRulechainRule;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.java.ast. *;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.java.ast.internal. *;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.java.types. *;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.java.symbols. *;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.ast.NodeStream;" + "\n"
                new_checker += line + "\n"
        new_checker = new_checker.strip()
        return new_checker

    def super_is_correctly_used(self, checker: str):
        new_checker = ""
        content = [line for line in checker.split("\n")]
        for line in content:
            if "super.addRuleChainVisit" in line:
                begin_index = line.index("super")
                end_index = line.index("(")
                line = line[:begin_index + 5] + line[end_index:]
            new_checker += line + "\n"
        new_checker = new_checker.strip()
        return new_checker

    def name_is_correctly_used(self, checker: str, rule_name: str):
        new_checker = ""
        content = [line for line in checker.split("\n")]
        for line in content:
            if "public class " in line and "extends" in line:
                begin_index = line.index("public")
                end_index = line.index("{")
                line = line[:begin_index] + rule_name + " " + line[end_index:]
            new_checker += line + "\n"
        new_checker = new_checker.strip()
        return new_checker

    def generate_checker_with_query(self, query: str):
        checker = None
        while checker is None:
            checker = self.run_llm(query)
            checker = parse_java_code_from_answer(checker)

        return checker

    def get_error_info(self, output: str):
        mvn_parser = MavenOutputParser()
        parsed_output = mvn_parser.parse(output)
        error_class = [entry for entry in parsed_output if "notfound_class" in entry]
        error_API = [entry for entry in parsed_output if "notfound_API" in entry]
        error_API_loc = [entry for entry in parsed_output if "notfound_API_location" in entry]
        # print(error_class)
        # print(error_API)
        # print(error_API_loc)
        error_info = ""

        if len(error_class) > 0:
            error_info = error_class[0]["notfound_class"] + " class is not correctly imported"
        elif len(error_API) > 0 and len(error_API_loc) > 0:
            error_info = error_API_loc[0]["notfound_API_location"]
            error_info = error_info + " 调用的API " + error_API[0]["notfound_API"] + " 不存在"

        # print(error_info)
        return error_info

    def savechecker(self, checker: str):
        with open("../base/checker.txt", 'w+', encoding='gbk') as file:
            file.write(checker)
    def iterative_generate(self, ruleGen: str):
        ast_classes = []
        checker_test = TestChecker("D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4/pmd-java")

        with open("../base/astnodeswithpackageinfo.txt", 'r', encoding='gbk') as file:
            content = file.readlines()
        content = [line.strip() for line in content]
        for line in content:
            ast_classes = line.split(", ")

        rule = ruleGen
        print("========================================== Rule " + str(
            rule) + " ===========================================")
        full_rule = "public class " + rule + " extends AbstractJavaRulechainRule"
        method_data = get_rule("../base/generatecheckerrulejson.json", full_rule)
        rule_category = method_data["rule_category"]
        rule_name = method_data["rule_name"]
        rule_description = method_data["rule_description"]
        rule_testcase_xml_filepath = method_data["rule_testcase_xml_filepath"]

        rule_package_path = rule_category.replace('.', '/')
        rule_path = "D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4/pmd-java/src/main/java/" + rule_package_path + "/"
        rule_path2 = "D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4-testsingle/pmd-pmd_releases-7.0.0-rc4/pmd-java/src/main/java/" + rule_package_path + "/"
        start_index = rule_name.find(" ") + 1
        start_index = rule_name.find(" ", start_index) + 1
        end_index = rule_name.find(" ", start_index)
        x = rule_name[start_index: end_index]
        self.global_rule_name = x
        rule_path = rule_path + x + ".java"
        rule_path2 = rule_path2 + x + ".java"
        i = str(x).find("Rule")
        j = x[:i]
        testClass = j + "Test"
        negativeNumber = countNegative(rule_testcase_xml_filepath)
        totalNumber = countTestcases(rule_testcase_xml_filepath)
        positiveNumber = totalNumber-negativeNumber
        print("一共 "+str(totalNumber)+" 个测试用例")
        print("正例 " + str(positiveNumber) + " 个")
        print("反例 " + str(negativeNumber) + " 个")

        avoid_error_API = []
        single_success = False
        round = 1
        while not single_success:
            if round > 5:
                print("5轮生成失败")
                break

            print("==========================第" + str(round) + "轮生成checker========================")
            round += 1

            # 第一次生成checker
            avoid_error_API_info = ""
            avoid_error_API = list(set(avoid_error_API))
            error_API_i = 1
            for single_error in avoid_error_API:
                avoid_error_API_info = avoid_error_API_info + str(error_API_i) + ": " + single_error + "\n"
                error_API_i += 1

            print("开始写checker")
            checker_query = self.checker_prompt.format(
                Rule_description=rule_description,
                rule_package=rule_category,
                rule_name=rule_name
            )
            print("==========================The_first_checker_query=========================")
            print(checker_query)
            checker = self.generate_checker_with_query(checker_query)

            self.savechecker(checker)
            run_result = jar_run(
                ["java", "-jar", "CodeToAST.jar", "checker",
                 "D:/JetBrains/pycharm/project/CheckerAutoGen/base/checker.txt",
                 "D:/JetBrains/pycharm/project/CheckerAutoGen/base/checker_ast.txt"],
                "D:/JetBrains/pycharm/project/CheckerAutoGen/base")

            if not run_result:
                single_success = False
                print("出现语法错误，这一轮舍弃，直接重新生成")
            else:

                checker = self.class_is_correctly_imported(checker, ast_classes)
                checker = self.super_is_correctly_used(checker)
                checker = self.name_is_correctly_used(checker, rule_name)
                print("==========5轮中每一轮为第一个测试用例生成的checker===============")
                print(checker)
                checker_test.create_test(rule_path, checker)
                print("第一个测试用例生成的checker开始编译")
                output, compile_success = checker_test.run_compile()
                # print(output)
                print("一开始编译是否通过：")
                print(compile_success)
                i = 1
                bak_checker = checker
                bak_output = output
                while not compile_success:
                    error_info = self.get_error_info(output)
                    if i > 2 or (i <= 2 and error_info == ""):
                        if i > 2:
                            print(
                                " ======================第一个测试用例生成的checker 2轮 内编译修复不成功，重新来一轮生成checker============")
                        else:
                            print(
                                "编译错误不在预期范围内，重新生成")
                        compile_success = False
                        single_success = False
                        break

                    if error_info != "":
                        i = i + 1
                        if "调用的API" in str(error_info):
                            avoid_error_API.append(error_info)
                        repair_query = self.repair_compile_error_prompt.format(
                            Rule_description=rule_description,
                            source_code=checker,
                            failed_info=error_info
                        )
                        print(
                            "=======================第一个测试用例生成的checker repair_compile_error_query======================")
                        print(repair_query)

                        checker = self.generate_checker_with_query(repair_query)
                        self.savechecker(checker)
                        run_result = jar_run(
                            ["java", "-jar", "CodeToAST.jar", "checker",
                             "D:/JetBrains/pycharm/project/CheckerAutoGen/base/checker.txt",
                             "D:/JetBrains/pycharm/project/CheckerAutoGen/base/checker_ast.txt"],
                            "D:/JetBrains/pycharm/project/CheckerAutoGen/base")

                        if run_result:
                            print("第 " + str(i) + "轮修复编译错误的结果")

                            checker = self.class_is_correctly_imported(checker, ast_classes)
                            checker = self.super_is_correctly_used(checker)
                            checker = self.name_is_correctly_used(checker, rule_name)

                            print(
                                "==========修复编译错误后的checker===============")
                            print(checker)
                            checker_test.create_test(rule_path, checker)
                            output, compile_success = checker_test.run_compile()
                            bak_checker = checker
                            bak_output = output
                            if not compile_success:
                                print("编译错误")
                        else:
                            print("出现语法错误，重新修复编译错误")
                            checker = bak_checker
                            output = bak_output
                            compile_success = False

                if compile_success:
                    print("编译通过")
                    single_success = True
