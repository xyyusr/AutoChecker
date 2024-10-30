import os
from subprocess import check_output, CalledProcessError, STDOUT


project_path = "D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4/pmd-java"

def maven_run(command, cwd):
    pwd = os.getcwd()
    try:
        if cwd is not None:
            os.chdir(cwd)
        output_bytes = check_output(command, stderr=STDOUT, cwd=cwd, shell=True)
        output = output_bytes.decode('gbk', errors='replace')
        success = True
    except CalledProcessError as e:
        output = e.output.decode('gbk', errors='replace')
        success = False
    finally:
        os.chdir(pwd)
    return output,success

def jar_run(command, cwd):
    pwd = os.getcwd()
    try:
        if cwd is not None:
            os.chdir(cwd)
        output_bytes = check_output(command, stderr=STDOUT, cwd=cwd, shell=True)
        output = output_bytes.decode('gbk', errors='replace')
        success = True
    except CalledProcessError as e:
        output = e.output.decode('gbk', errors='replace')
        success = False
    finally:
        os.chdir(pwd)
    return success


# jar_run(["java", "-jar", "AnalyzeSourceCodeASTComplexity.jar", "D:/JetBrains/IdeaProjects/pmd-pmd_releases-7.0.0-rc4/pmd-java/src/test/resources/net/sourceforge/pmd/lang/java/rule/errorprone/xml/OverrideBothEqualsAndHashcode.xml"],
#                 "D:/JetBrains/pycharm/project/CheckerAutoGen/base")
# jar_run(["java", "-jar", "CodeToAST.jar", "D:/JetBrains/pycharm/project/CheckerAutoGen/testcase/onecode.xml",
#                  "D:/JetBrains/pycharm/project/CheckerAutoGen/testcase/ast.txt"],
#                 "D:/JetBrains/pycharm/project/CheckerAutoGen/base")