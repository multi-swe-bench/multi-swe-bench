from typing import Optional

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest


class ImageDefault(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> str:
        return "python:3.7-slim"
    
    def image_prefix(self) -> str:
        return "envagent"
       
    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        # Get test directory from PR object, default to a common pyscf test pattern if not available
        test_dir = getattr(self.pr, 'test_directory', None)
        
        # Handle multiple test directories separated by commas
        if ',' in test_dir:
            test_dirs = [d.strip() for d in test_dir.split(',')]
            test_dir_cmd = ' '.join(test_dirs)
        else:
            test_dir_cmd = test_dir
        
        return [
            File(
                ".",
                "fix.patch",
                f"{self.pr.fix_patch}",
            ),
            File(
                ".",
                "test.patch",
                f"{self.pr.test_patch}",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
python -m pytest {test_dir} --no-header -rA --tb=no -p no:cacheprovider
""".format(
                    pr=self.pr,
                    test_dir=test_dir_cmd
                ),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
python -m pytest {test_dir} --no-header -rA --tb=no -p no:cacheprovider
""".format(
                    pr=self.pr,
                    test_dir=test_dir_cmd
                ),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
python -m pytest {test_dir} --no-header -rA --tb=no -p no:cacheprovider

""".format(
                    pr=self.pr,
                    test_dir=test_dir_cmd
                ),
            ),
        ]

    def dockerfile(self) -> str:
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"


        pyscf_version = getattr(self.pr, 'version', None)
        print(f"PySCF version from dataset: {pyscf_version}")
        pyscf_version = "2.7.0"

        print(self.pr.base.sha)
            
        
        dockerfile_content = f"""
        FROM titouandu/pyscf-build:{pyscf_version}

        WORKDIR /home/pyscf

        RUN git fetch origin && \
            git fetch --no-tags origin "pull/{self.pr.number}/head:pr-{self.pr.number}" && \
            git checkout {self.pr.base.sha}

        """ 

        dockerfile_content += f"""{copy_commands}"""



        
        return dockerfile_content.format(pr=self.pr)


@Instance.register("pyscf", "pyscf")
class PYSCF(Instance):
    def __init__(self, pr: PullRequest, config: Config, *args, **kwargs):
        super().__init__()
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    def dependency(self) -> Optional[Image]:
        return ImageDefault(self.pr, self._config)

    def run(self, run_cmd: str = "") -> str:
        if run_cmd:
            return run_cmd

        return 'bash /home/run.sh'

    def test_patch_run(self, test_patch_run_cmd: str = "") -> str:
        if test_patch_run_cmd:
            return test_patch_run_cmd

        return "bash /home/test-run.sh"

    def fix_patch_run(self, fix_patch_run_cmd: str = "") -> str:
        if fix_patch_run_cmd:
            return fix_patch_run_cmd

        return "bash /home/fix-run.sh"


    def parse_log(self, log: str) -> TestResult:
        # Parse the log content and extract test execution results.
        passed_tests = set() 
        failed_tests = set() 
        skipped_tests = set() 
        import re
        import json
        for line in log.splitlines():
            if line.startswith("PASSED"):
                match = re.match(r"PASSED\s+(.*)", line)
                if match:
                    passed_tests.add(match.group(1).strip())
            elif line.startswith("FAILED"):
                match = re.match(r"FAILED\s+([^\s-]+)", line)
                if match:
                    failed_tests.add(match.group(1).strip())
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests
        }
        

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )