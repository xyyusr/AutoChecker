import sys
import time
from AutoCheckerGenerator import CheckerGenerator
import shutil
from getRule import get_rule
from testrule import TestChecker

easy_rules = ["AvoidUsingOctalValuesRule","ExcessiveImportsRule","NullAssignmentRule","IdenticalCatchBranchesRule",
          "InefficientEmptyStringCheckRule","SignatureDeclareThrowsExceptionRule","StringInstantiationRule","UseStringBufferForStringAppendsRule",
               "ExceptionAsFlowControlRule","ExcessivePublicCountRule"]
not_easy_rules = ["LiteralsFirstInComparisonsRule","MethodNamingConventionsRule","UnnecessaryImportRule","AssignmentToNonFinalStaticRule","AvoidDuplicateLiteralsRule",
    "AvoidThrowingNullPointerExceptionRule","EmptyControlStatementRule","BrokenNullCheckRule","AvoidInstantiatingObjectsInLoopsRule",
                  "ClassWithOnlyPrivateConstructorsShouldBeFinalRule"]

generator = CheckerGenerator(
    "",  # your openai_key
    '' # model, like GPT-4
)

# 此工具根目录
AutoChecker="xx/AutoChecker"

# pmd仓库下载地址 https://github.com/pmd/pmd/tree/pmd_releases/7.0.0-rc4
pmd_project = "pmd-loc1/pmd-java"
another_pmd_project = "pmd-loc2/pmd-java"

checker_test = TestChecker(pmd_project) # test checker on full test set excluding skipped test cases to looking for next failed test case
checker_single_test = TestChecker(another_pmd_project) # test checker on candidate test pool to judge whether the checker is correct

original_stdout = sys.stdout

for rule in easy_rules:
    print(rule)
    file = "output/" + rule + ".txt" # txt file to store log info
    full_rule = "public class " + rule + " extends AbstractJavaRulechainRule"
    method_data = get_rule("../../experiment/Experimental_20rules.json", full_rule)
    rule_testcase_xml_filepath = pmd_project+method_data["rule_testcase_xml_filepath"]

    # reset the checkers and test case sets in two pmd projects
    src_folder = pmd_project + "/src/main/java/net/sourceforge/pmd/lang/java/rule"
    dest_folder = "../../experiment/pmd-checkers/rule"
    shutil.rmtree(src_folder)
    shutil.copytree(dest_folder, src_folder)
    src_folder = another_pmd_project + "/src/main/java/net/sourceforge/pmd/lang/java/rule"
    shutil.rmtree(src_folder)
    shutil.copytree(dest_folder, src_folder)

    src_xml = rule_testcase_xml_filepath
    index = rule.find("Rule")
    dest_xml = "../../experiment/experimental-20rules-test-suite/easy/"+rule[:index]+".xml"
    shutil.copyfile(dest_xml, src_xml)

    # ensure two projects compile successfully
    output1, compile_success1 = checker_test.run_compile()
    output2, compile_success2 = checker_single_test.run_compile()

    if compile_success1 and compile_success2:
        with open(file, 'w+') as f:
            sys.stdout = f
            print("begin")
            print()
            time1 = time.time()
            generator.iterative_generate(rule,pmd_project,another_pmd_project,AutoChecker)
            time2 = time.time()
            print("end")
            print()
            execution_time = time2 - time1
            print("time cost: " + str(execution_time) + " seconds")
    else:
        break
    sys.stdout = original_stdout
sys.stdout = original_stdout