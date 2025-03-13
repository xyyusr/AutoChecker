import sys
import time
from tool.generator.AutoCheckerGenerator import CheckerGenerator
import shutil
from tool.generator.getRule import get_rule
from tool.generator.testrule import TestChecker

easy_rules = ["AvoidUsingOctalValuesRule","ExcessiveImportsRule","NullAssignmentRule","IdenticalCatchBranchesRule",
          "InefficientEmptyStringCheckRule","SignatureDeclareThrowsExceptionRule","StringInstantiationRule","UseStringBufferForStringAppendsRule",
               "ExceptionAsFlowControlRule","ExcessivePublicCountRule"]
not_easy_rules = ["LiteralsFirstInComparisonsRule","MethodNamingConventionsRule","UnnecessaryImportRule","AssignmentToNonFinalStaticRule","AvoidDuplicateLiteralsRule",
    "AvoidThrowingNullPointerExceptionRule","EmptyControlStatementRule","BrokenNullCheckRule","AvoidInstantiatingObjectsInLoopsRule",
                  "ClassWithOnlyPrivateConstructorsShouldBeFinalRule"]

generator = CheckerGenerator(
    "",  # your openai_key
    ''  # model, like GPT-4
)

checker_test = TestChecker("your-pmd-loc/pmd-java")
checker_single_test = TestChecker(
                "your-another-pmd-loc/pmd-java")

original_stdout = sys.stdout

for rule in easy_rules:
    print(str(rule)+"start")
    file = "../experiment/autochecker/GPT-4-GPT-4-GPT-4-GPT-4-GPT-4-results/easy/"+rule+".txt"

    full_rule = "public class " + rule + " extends AbstractJavaRulechainRule"
    method_data = get_rule("../experiment/Experimental_20rules.json", full_rule)
    rule_testcase_xml_filepath = method_data["rule_testcase_xml_filepath"]

    src_folder = "your-pmd-loc/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule"

    dest_folder = "xx/rule"

    shutil.rmtree(src_folder)

    shutil.copytree(dest_folder, src_folder)

    src_folder = "your-another-pmd-loc/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule"

    shutil.rmtree(src_folder)

    shutil.copytree(dest_folder, src_folder)

    src_xml = rule_testcase_xml_filepath

    index = rule.find("Rule")

    dest_xml = "../experiment/experimental-20rules-test-suite/easy/"+rule[:index]+".xml"

    shutil.copyfile(dest_xml, src_xml)

    output1, compile_success1 = checker_test.run_compile()
    output2, compile_success2 = checker_single_test.run_compile()

    if compile_success1 and compile_success2:
        with open(file, 'w+') as f:

            sys.stdout = f

            print("begin")
            print()

            time1 = time.time()
            generator.iterative_generate(rule)
            time2 = time.time()

            print("end")
            print()

            execution_time = time2 - time1
            print("time cost: " + str(execution_time) + " seconds")

    else:
        break

    sys.stdout = original_stdout


sys.stdout = original_stdout

for rule in not_easy_rules:

    print(str(rule)+"start")

    file = "../experiment/autochecker/GPT-4-GPT-4-GPT-4-GPT-4-GPT-4-results/not easy/"+rule+".txt"

    full_rule = "public class " + rule + " extends AbstractJavaRulechainRule"
    method_data = get_rule("../experiment/Experimental_20rules.json", full_rule)
    rule_testcase_xml_filepath = method_data["rule_testcase_xml_filepath"]

    src_folder = "your-pmd-loc/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule"

    dest_folder = "xx/rule"

    shutil.rmtree(src_folder)

    shutil.copytree(dest_folder, src_folder)

    src_folder = "your-another-pmd-loc/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule"

    shutil.rmtree(src_folder)

    shutil.copytree(dest_folder, src_folder)

    src_xml = rule_testcase_xml_filepath

    index = rule.find("Rule")

    dest_xml = "../experiment/experimental-20rules-test-suite/not easy/"+rule[:index]+".xml"

    shutil.copyfile(dest_xml, src_xml)

    output1, compile_success1 = checker_test.run_compile()
    output2, compile_success2 = checker_single_test.run_compile()

    if compile_success1 and compile_success2:
        with open(file, 'w+') as f:

            sys.stdout = f

            print("begin")
            print()

            time1 = time.time()
            generator.iterative_generate(rule)
            time2 = time.time()

            print("end")
            print()

            execution_time = time2 - time1
            print("time cost: " + str(execution_time) + " seconds")

    else:
        break

    sys.stdout = original_stdout

sys.stdout = original_stdout

