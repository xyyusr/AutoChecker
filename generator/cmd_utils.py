import os
from subprocess import check_output, CalledProcessError, STDOUT


project_path = "your-pmd-loc/pmd-java"

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