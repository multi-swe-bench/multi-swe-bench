import re
import json
from typing import Optional, Union

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
        return "ubuntu:latest"
    
    def image_prefix(self) -> str:
        return "envagent"
       
    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        repo_name= self.pr.repo
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
                "prepare.sh",
                """ls
###ACTION_DELIMITER###
apt-get update && apt-get install -y golang
###ACTION_DELIMITER###
curl -L -O https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.14.0/kubebuilder_linux_amd64.tar.gz && tar -zxvf kubebuilder_linux_amd64.tar.gz && mv kubebuilder/bin/* /usr/local/bin/
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
curl -L -O https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.14.0/kubebuilder_linux_amd64.tar.gz && tar -zxvf kubebuilder_linux_amd64.tar.gz && mv kubebuilder/bin/* /usr/local/bin/
###ACTION_DELIMITER###
curl -L -O https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.14.0/kubebuilder_3.14.0_linux_amd64.tar.gz && tar -zxvf kubebuilder_3.14.0_linux_amd64.tar.gz && mv kubebuilder_3.14.0_linux_amd64/bin/* /usr/local/bin/
###ACTION_DELIMITER###
curl -L -O https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.14.0/kubebuilder_linux_amd64.tar.gz && tar -zxvf kubebuilder_linux_amd64.tar.gz && mv kubebuilder/bin/* /usr/local/bin/
###ACTION_DELIMITER###
go install sigs.k8s.io/kubebuilder/v3/cmd/kubebuilder@v3.14.0 && cp $(go env GOPATH)/bin/kubebuilder /usr/local/bin/
###ACTION_DELIMITER###
curl -LO https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.14.0/kubebuilder_3.14.0_linux_amd64.tar.gz && tar -zxvf kubebuilder_3.14.0_linux_amd64.tar.gz && mv kubebuilder_3.14.0_linux_amd64/bin/* /usr/local/bin/
###ACTION_DELIMITER###
wget https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.13.0/kubebuilder_linux_amd64.tar.gz && tar -zxvf kubebuilder_linux_amd64.tar.gz && mv kubebuilder/bin/* /usr/local/bin/
###ACTION_DELIMITER###
curl -L https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.14.0/kubebuilder_$(go env GOOS)_$(go env GOARCH).tar.gz | tar -xz -C /tmp/ && mv /tmp/kubebuilder_$(go env GOOS)_$(go env GOARCH) /usr/local/kubebuilder && export PATH=$PATH:/usr/local/kubebuilder/bin && ln -s /usr/local/kubebuilder/bin/kubebuilder /usr/local/bin/
###ACTION_DELIMITER###
curl -L -O https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.14.0/kubebuilder_3.14.0_linux_amd64.tar.gz && tar -zxvf kubebuilder_3.14.0_linux_amd64.tar.gz && mv kubebuilder_3.14.0_linux_amd64/bin/* /usr/local/bin/
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
apt-get update && apt-get install -y make
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
go install sigs.k8s.io/controller-tools/cmd/controller-gen@v0.3.0 && cp $(go env GOPATH)/bin/controller-gen /usr/local/bin/
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
go install sigs.k8s.io/controller-tools/cmd/controller-gen@v0.14.0 && cp $(go env GOPATH)/bin/controller-gen /usr/local/bin/
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
go install sigs.k8s.io/controller-tools/cmd/controller-gen@v0.4.1 && cp $(go env GOPATH)/bin/controller-gen /usr/local/bin/
###ACTION_DELIMITER###
wget https://dl.google.com/go/go1.13.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.13.linux-amd64.tar.gz && export PATH=/usr/local/go/bin:$PATH && go version
###ACTION_DELIMITER###
curl -O https://dl.google.com/go/go1.13.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.13.linux-amd64.tar.gz && export PATH=/usr/local/go/bin:$PATH && go version
###ACTION_DELIMITER###
go mod download && make test
###ACTION_DELIMITER###
sed -i 's/go 1.13/go 1.14/' go.mod && go mod tidy && make test
###ACTION_DELIMITER###
curl -O https://dl.google.com/go/go1.14.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.14.linux-amd64.tar.gz && export PATH=/usr/local/go/bin:$PATH && go version && go mod tidy && make test
###ACTION_DELIMITER###
rm -rf /usr/local/go && curl -O https://dl.google.com/go/go1.14.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.14.linux-amd64.tar.gz && export PATH=/usr/local/go/bin:$PATH && go version && go mod tidy && make test
###ACTION_DELIMITER###
go test ./pkg/... ./cmd/... -v
###ACTION_DELIMITER###
curl -L -O https://github.com/kubernetes-sigs/kubebuilder/releases/download/v2.3.1/kubebuilder_2.3.1_linux_amd64.tar.gz && tar -zxvf kubebuilder_2.3.1_linux_amd64.tar.gz && mv kubebuilder_2.3.1_linux_amd64 /usr/local/kubebuilder && export PATH=$PATH:/usr/local/kubebuilder/bin && kubebuilder version
###ACTION_DELIMITER###
export KUBEBUILDER_ASSETS=/usr/local/kubebuilder/bin && go test ./pkg/... ./cmd/... -v
###ACTION_DELIMITER###
echo 'go test -v -count=1 ./pkg/... ./cmd/...' > /home/kserve/test_commands.sh && chmod +x /home/kserve/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
go test -v -count=1 ./pkg/... ./cmd/...

""".replace("[[REPO_NAME]]", repo_name)
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
go test -v -count=1 ./pkg/... ./cmd/...

""".replace("[[REPO_NAME]]", repo_name)
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
if ! git -C /home/[[REPO_NAME]] apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
go test -v -count=1 ./pkg/... ./cmd/...

""".replace("[[REPO_NAME]]", repo_name)
            ),
        ]

    def dockerfile(self) -> str:
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        dockerfile_content = """
# This is a template for creating a Dockerfile to test patches
# LLM should fill in the appropriate values based on the context

# Choose an appropriate base image based on the project's requirements - replace ubuntu:latest with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM ubuntu:latest

## Set noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Install basic requirements
# For example: RUN apt-get update && apt-get install -y git
# For example: RUN yum install -y git
# For example: RUN apk add --no-cache git
RUN apt-get update && apt-get install -y git

# Ensure bash is available
RUN if [ ! -f /bin/bash ]; then         if command -v apk >/dev/null 2>&1; then             apk add --no-cache bash;         elif command -v apt-get >/dev/null 2>&1; then             apt-get update && apt-get install -y bash;         elif command -v yum >/dev/null 2>&1; then             yum install -y bash;         else             exit 1;         fi     fi

WORKDIR /home/
COPY fix.patch /home/
COPY test.patch /home/
RUN git clone https://github.com/kserve/kserve.git /home/kserve

WORKDIR /home/kserve
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("kserve", "kserve_1518_to_1281")
class KSERVE_1518_TO_1281(Instance):
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
        passed_tests = set()  # Tests that passed successfully
        failed_tests = set()  # Tests that failed
        skipped_tests = set()  # Tests that were skipped
        import re
        import json
        # Use regex to find test results
        test_pattern = re.compile(r'--- (PASS|FAIL|SKIPPED): (\S+)')
        matches = test_pattern.findall(log)
        for status, test_name in matches:
            if status == 'PASS':
                passed_tests.add(test_name)
            elif status == 'FAIL':
                failed_tests.add(test_name)
            elif status == 'SKIPPED':
                skipped_tests.add(test_name)
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
