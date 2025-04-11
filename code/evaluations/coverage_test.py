import os
import re
import subprocess
import logging
from bs4 import BeautifulSoup

import tools.io_utils as utils


class ProjrctTestRunner:
    project_info: dict
    cd_cmd: list
    testclass_path: str
    report_path: str
    test_result: dict

    def __init__(self, project_info, dep_fd, tc_path, rpt_path):
        self.logger = logging.getLogger(__name__)
        self.project_info = project_info
        self.cd_cmd = ['cd', project_info["project-url"], '&&']
        self.dependency_fd = dep_fd
        self.testclass_path = tc_path.replace("<project>",project_info["project-name"])
        self.report_path = rpt_path.replace("<project>",project_info["project-name"])

    def run_project_test(self, compile=True):
        project_name = self.project_info["project-name"]
        project_url = self.project_info["project-url"]
        test_objects = self.project_info["focused-methods"]
        failed_tests = {}
        self.test_result = {}

        self.logger.info(f"Running tests for project: {project_name}")
        for tobject in test_objects:
            test_class = tobject["test-class"]
            test_path = tobject["test-path"]
            testid = tobject["id"]
            class_path = f"{self.testclass_path}/{test_path.split('/')[-1]}"
            utils.copy_file(class_path, f"{project_url}/{test_path}")
            if compile and not self.compile_test(test_path):
                failed_tests[testid] = "compile error"
                continue
            if not self.run_singal_unit_test(testid, test_class):
                failed_tests[testid] = "execution error"
                continue
            # todo: add test pass rate
            if not self.generate_report_single(testid):
                failed_tests[testid] = "report error"
        return failed_tests, self.test_result

    def compile_test(self, class_path):
        compile_cmd = ["javac","-cp","@dependencies.txt","-d","target/test-classes",class_path]
        self.logger.info(" ".join(compile_cmd))
        script = self.cd_cmd + compile_cmd
        result = subprocess.run(script, capture_output=True, text=True, shell=True)
        if result.returncode!= 0:
            self.logger.error(f"error occured in compile test class, info:\n{result.stderr}")
            return False
        return True

    def get_pass_rate(self, test_info):
        cases = int(re.findall(r"([0-9]+) tests started", test_info)[0])
        passed = int(re.findall(r"([0-9]+) tests successful", test_info)[0])
        return (cases, passed)

    def run_singal_unit_test(self, testid, testclass):
        self.logger.info(f"Running single unit test, testclass: {testclass}")
        test_dependencies = f"libs/*;target/test-classes;target/classes;{self.dependency_fd}/*"
        java_agent = f"-javaagent:{self.dependency_fd}/jacocoagent.jar=destfile=target/jacoco.exec"
        test_cmd = ['java', '-cp', test_dependencies, java_agent, 'org.junit.platform.console.ConsoleLauncher', '--disable-banner', '--disable-ansi-colors', '--fail-if-no-tests', '--select-class', testclass]
        script = self.cd_cmd + test_cmd
        result = subprocess.run(script, capture_output=True, text=True, shell=True)
        test_info = result.stdout
        if result.returncode == 2:
            self.logger.info(f"test execution info: {test_info}")
            test_cases, passed_cases = self.get_pass_rate(test_info)
            self.test_result[testid] = {"test_cases": test_cases, "passed_cases": passed_cases}
            return True
        elif test_info.find("Test run finished")!=-1:
            self.logger.warning("return code: ", result.returncode)
            self.logger.warning(f"test case failed in {testclass}, info:\n{result.stderr}\n{test_info}")
            test_cases, passed_cases = self.get_pass_rate(test_info)
            self.test_result[testid] = {"test_cases": test_cases, "passed_cases": passed_cases}
            return True
        else:
            self.logger.error(f"error occured in execute test class {testclass}, info:\n{result.stderr}\n{test_info}")
            return False

    def generate_report_single(self, testid):
        # generate report
        jacoco_cli = f"{self.dependency_fd}/jacococli.jar"
        html_report = f"{self.report_path}/jacoco-report-html/{testid}/"
        csv_report = f"{self.report_path}/jacoco-report-csv/{testid}.csv"
        # report_cmd = ['java', '-jar', jacoco_cli, "report", "target/jacoco.exec", "--classfiles", "target/classes", "--html", html_report, "--csv", csv_report]
        report_cmd = ['java', '-jar', jacoco_cli, "report", "target/jacoco.exec", '--classfiles', 'target/classes', '--sourcefiles', 'src/main/java', "--html", html_report, "--csv", csv_report]
        script = self.cd_cmd + report_cmd
        result = subprocess.run(script, capture_output=True, text=True, shell=True)

        if result.returncode!= 0:
            self.logger.error(f"error occured in generate report, info:\n{result.stderr}")
            return False
        return True


class CoverageExtractor:

    project_info: dict

    def __init__(self, project_info, rpt_path):
        self.project_info = project_info
        self.report_path = rpt_path.replace("<project>",project_info["project-name"])
        self.logger = logging.getLogger(__name__)

    def extract_single_coverage(self, testid, package, classname, method):
        # extract coverage
        self.logger.info(f"Extracting coverage for class: {classname}, method: {method}")
        coverage_score = None
        html_path = f"{self.report_path}/jacoco-report-html/{testid}/{package}/{classname}.html"
        if not os.path.exists(html_path):
            self.logger.exception(f"report file not found: {html_path}")
            return coverage_score
        
        with open(html_path, "r") as file:
            soup = BeautifulSoup(file, 'lxml-xml')
        for tr in soup.find_all(name='tbody')[0].find_all(name='tr', recursive=False):
            tds = tr.contents
            try:
                method_name = tds[0].span.string
            except AttributeError:
                method_name = tds[0].a.string
            # encode(byte[], int, int, BaseNCodec.Context)
            method = " ".join(method_parts).replace("(", "( ")
            method_parts = [ part.split(".")[-1] if "." in part else part
                for part in method_name.split()
            ]
            method = " ".join(method_parts).replace("( ", "(")
            if method_name != method: continue
            instruction_cov = float(tds[2].string.replace("%", ""))/100
            branch_cov = float(tds[4].string.replace("%", ""))/100
            coverage_score = {"inst_cov": instruction_cov, "bran_cov": branch_cov}
            break
        # return coverage results
        return coverage_score

    def extract_coverage_project(self, failed_tests:dict, test_result:dict):
        """
        result format:
        {   
            "<class_name>#{method_name}": {
                "error_type": <error type>
            },
            "<class_name>#{method_name}": {
                "test_cases": number, 
                "passed_cases": number,
                "inst_cov": <instruction coverage>,
                "bran_cov": <branch coverage>
            }
        }
        """
        focused_methods = self.project_info["focused-methods"]
        summary = test_result.copy()
        for test in focused_methods:
            testid = test["id"]
            method = test["method-name"]
            if testid in failed_tests:
                error_info = failed_tests[testid]
                summary[f"{test['class']}#{method}"] = { "error_type": error_info}
            else:
                package = test["package"]
                classname = test["class"].split(".")[-1]
                cov_score = self.extract_single_coverage(testid, package, classname, method)
                data_id = f"{test['class']}#{method}"
                if cov_score: 
                    summary[data_id].update(cov_score)
                else: 
                    summary[data_id].update({"inst_cov": "<missing>", "bran_cov": "<missing>"})
        return summary


def test_coverage(fstruct, task_setting, dataset_info: dict):
    root_path = fstruct.ROOT_PATH
    dataset_dir = f"{root_path}/{fstruct.DATASET_PATH}"
    testclass_path = f"{root_path}/{fstruct.TESTCLASSS_PATH}"
    report_path = f"{root_path}/{fstruct.REPORT_PATH}"
    dependency_dir = f"{root_path}/{fstruct.DEPENDENCY_PATH}"
    compile_test = task_setting.COMPILE_TEST

    for pj_name, info in dataset_info.items():
        project_path = f"{dataset_dir}/{info['project-url']}"
        info["project-url"] = project_path
        # run converage test & generate report
        runner = ProjrctTestRunner(info, dependency_dir, testclass_path, report_path)
        failed_tests, test_result = runner.run_project_test(compile_test)
        # extract coverage
        extractor = CoverageExtractor(info, report_path)
        coverage_data = extractor.extract_coverage_project(failed_tests, test_result)
        print(f"report data:\n{coverage_data}")
        coverage_file = f"{report_path}/summary.json".replace("<project>", pj_name)
        utils.write_json(coverage_file, coverage_data)
    return

# test
if __name__ == "__main__":

    project_path = "../dataset/puts/commons-csv"
    test_runner = ProjrctTestRunner(project_path)
    class_path = "org.jacoco.examples"
    class_name = "QrConfig"
    method_name = "toHints(BarcodeFormat)"
    testclass = "org.jacoco.examples.MethodHandleUtilTest"
    test_response = test_runner.run_singal_unit_test(testclass)
    print(test_response)
    pass
