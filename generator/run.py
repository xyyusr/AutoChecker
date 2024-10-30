import sys
import time
from generator.AutoCheckerGenerator import CheckerGenerator
import shutil
from generator.getRule import get_rule
from generator.testrule import TestChecker

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

checker_test = TestChecker("D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4/pmd-java")
checker_single_test = TestChecker(
                "D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4-testsingle/pmd-pmd_releases-7.0.0-rc4/pmd-java")

# 保存原始的标准输出流
original_stdout = sys.stdout

flag=1

for rule in easy_rules:
    print(str(rule)+"开始")
    # 打开文件，准备写入数据
    file = "../experiment/autochecker/results/easy/"+rule+".txt"

    full_rule = "public class " + rule + " extends AbstractJavaRulechainRule"
    method_data = get_rule("../base/generatecheckerrulejson.json", full_rule)
    rule_testcase_xml_filepath = method_data["rule_testcase_xml_filepath"]

    # 原文件夹路径
    src_folder = "D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule"

    # 新文件夹路径
    dest_folder = "C:/Users/XYY/Desktop/rule"

    # 删除原文件夹
    shutil.rmtree(src_folder)

    # 复制新文件夹到原文件夹位置
    shutil.copytree(dest_folder, src_folder)

    # 原文件夹路径
    src_folder = "D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4-testsingle/pmd-pmd_releases-7.0.0-rc4/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule"

    # 删除原文件夹
    shutil.rmtree(src_folder)

    # 复制新文件夹到原文件夹位置
    shutil.copytree(dest_folder, src_folder)

    # 原XML文件路径
    src_xml = rule_testcase_xml_filepath

    index = rule.find("Rule")
    # 新XML文件路径
    dest_xml = "../experiment/rules/easy/"+rule[:index]+".xml"

    # 复制新XML文件到原XML文件位置，实现替换
    shutil.copyfile(dest_xml, src_xml)

    output1, compile_success1 = checker_test.run_compile()
    output2, compile_success2 = checker_single_test.run_compile()

    if compile_success1 and compile_success2:
        with open(file, 'w+') as f:

            # 将标准输出流重定向到文件对象
            sys.stdout = f

            print("开始")
            print()

            # 记录开始时间
            time1 = time.time()
            generator.iterative_generate(rule)
            # 记录结束时间
            time2 = time.time()

            print("结束")
            print()
            # 计算程序执行时间
            execution_time = time2 - time1
            print("规则执行完毕，时间总花销： " + str(execution_time) + " 秒")

    else:
        flag=0
        break

    sys.stdout = original_stdout

# 恢复原始的标准输出流
sys.stdout = original_stdout

if flag == 0:
    print("easy编译发生错误")
else:
    print("easy全部执行成功")


flag=1

for rule in not_easy_rules:

    print(str(rule)+"开始")
    # 打开文件，准备写入数据
    file = "../experiment/autochecker/results/not easy/"+rule+".txt"

    full_rule = "public class " + rule + " extends AbstractJavaRulechainRule"
    method_data = get_rule("../base/generatecheckerrulejson.json", full_rule)
    rule_testcase_xml_filepath = method_data["rule_testcase_xml_filepath"]

    # 原文件夹路径
    src_folder = "D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule"

    # 新文件夹路径
    dest_folder = "C:/Users/XYY/Desktop/rule"

    # 删除原文件夹
    shutil.rmtree(src_folder)

    # 复制新文件夹到原文件夹位置
    shutil.copytree(dest_folder, src_folder)

    # 原文件夹路径
    src_folder = "D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4-testsingle/pmd-pmd_releases-7.0.0-rc4/pmd-java/src/main/java/net/sourceforge/pmd/lang/java/rule"

    # 删除原文件夹
    shutil.rmtree(src_folder)

    # 复制新文件夹到原文件夹位置
    shutil.copytree(dest_folder, src_folder)

    # 原XML文件路径
    src_xml = rule_testcase_xml_filepath

    index = rule.find("Rule")
    # 新XML文件路径
    dest_xml = "../experiment/rules/not easy/"+rule[:index]+".xml"

    # 复制新XML文件到原XML文件位置，实现替换
    shutil.copyfile(dest_xml, src_xml)

    output1, compile_success1 = checker_test.run_compile()
    output2, compile_success2 = checker_single_test.run_compile()

    if compile_success1 and compile_success2:
        with open(file, 'w+') as f:

            # 将标准输出流重定向到文件对象
            sys.stdout = f

            print("开始")
            print()

            # 记录开始时间
            time1 = time.time()
            generator.iterative_generate(rule)
            # 记录结束时间
            time2 = time.time()

            print("结束")
            print()
            # 计算程序执行时间
            execution_time = time2 - time1
            print("规则执行完毕，时间总花销： " + str(execution_time) + " 秒")

    else:
        flag=0
        break

    sys.stdout = original_stdout

# 恢复原始的标准输出流
sys.stdout = original_stdout

if flag == 0:
    print("not easy编译发生错误")
else:
    print("not easy全部执行成功")

