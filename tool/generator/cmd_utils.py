import os
from subprocess import check_output, CalledProcessError, STDOUT


def maven_run(command, cwd):
    pwd = os.getcwd()
    try:
        if cwd is not None:
            os.chdir(cwd)
        output_bytes = check_output(command, stderr=STDOUT, cwd=cwd, shell=True)
        output = output_bytes.decode('utf-8', errors='replace')
        success = True
    except CalledProcessError as e:
        output = e.output.decode('utf-8', errors='replace')
        success = False
    finally:
        os.chdir(pwd)
    return output,success

def jar_run(command, cwd):
    pwd = os.getcwd()
    try:
        if cwd is not None:
            os.chdir(cwd)
        check_output(command, stderr=STDOUT, cwd=cwd, shell=True)
        success = True
    except CalledProcessError as e:
        success = False
    finally:
        os.chdir(pwd)
    return success