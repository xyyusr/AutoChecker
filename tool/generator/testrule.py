from tool.generator.cmd_utils import maven_run
import os

class TestChecker(object):
    def __init__(self, project_path: str) -> None:
        self.project_path = project_path

    def create_test(self, path: str, content: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def remove_test(self, path: str):
        os.remove(path)

    def run_tests(self, rule: str):
        output, success = maven_run(["mvn", "test", "-Dtest="+rule], self.project_path)
        return output, success

    def run_compile(self):
        maven_run(["mvn", "clean"], self.project_path)
        output, success = maven_run(["mvn", "compile"], self.project_path)
        return output, success