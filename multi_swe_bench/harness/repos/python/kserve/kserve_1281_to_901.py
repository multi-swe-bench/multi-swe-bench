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
        return "python:3.9-slim"
    
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
                """ls -la
###ACTION_DELIMITER###
apt-get update && apt-get install -y golang
###ACTION_DELIMITER###
ls hack/
###ACTION_DELIMITER###
go mod download
###ACTION_DELIMITER###
ls python/
###ACTION_DELIMITER###
go test -v ./pkg/... ./cmd/... -coverprofile coverage.out
###ACTION_DELIMITER###
wget https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.11.0/kubebuilder_linux_amd64.tar.gz && tar -zxvf kubebuilder_linux_amd64.tar.gz && mv kubebuilder /usr/local && export KUBEBUILDER_ASSETS=/usr/local/kubebuilder/bin
###ACTION_DELIMITER###
apt-get update && apt-get install -y wget
###ACTION_DELIMITER###
wget https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.11.0/kubebuilder_linux_amd64.tar.gz && tar -zxvf kubebuilder_linux_amd64.tar.gz && mv kubebuilder /usr/local && export KUBEBUILDER_ASSETS=/usr/local/kubebuilder/bin
###ACTION_DELIMITER###
wget https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.10.0/kubebuilder_linux_amd64.tar.gz && tar -zxvf kubebuilder_linux_amd64.tar.gz && mv kubebuilder /usr/local && export KUBEBUILDER_ASSETS=/usr/local/kubebuilder/bin
###ACTION_DELIMITER###
wget https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.14.0/kubebuilder_linux_amd64.tar.gz && tar -zxvf kubebuilder_linux_amd64.tar.gz && mv kubebuilder_3.14.0_linux_amd64 /usr/local/kubebuilder && export KUBEBUILDER_ASSETS=/usr/local/kubebuilder/bin
###ACTION_DELIMITER###
wget https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.14.0/kubebuilder_v3.14.0_linux_amd64.tar.gz && tar -zxvf kubebuilder_v3.14.0_linux_amd64.tar.gz && mv kubebuilder_v3.14.0_linux_amd64 /usr/local/kubebuilder && export KUBEBUILDER_ASSETS=/usr/local/kubebuilder/bin
###ACTION_DELIMITER###
wget https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.13.0/kubebuilder_linux_amd64.tar.gz && tar -zxvf kubebuilder_linux_amd64.tar.gz && mv kubebuilder_3.13.0_linux_amd64 /usr/local/kubebuilder && export KUBEBUILDER_ASSETS=/usr/local/kubebuilder/bin
###ACTION_DELIMITER###
wget https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.14.0/kubebuilder_3.14.0_linux_amd64.tar.gz && tar -zxvf kubebuilder_3.14.0_linux_amd64.tar.gz && mv kubebuilder_3.14.0_linux_amd64 /usr/local/kubebuilder && export KUBEBUILDER_ASSETS=/usr/local/kubebuilder/bin
###ACTION_DELIMITER###
wget https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.9.0/kubebuilder_linux_amd64.tar.gz && tar -zxvf kubebuilder_linux_amd64.tar.gz && mv kubebuilder /usr/local && export KUBEBUILDER_ASSETS=/usr/local/kubebuilder/bin
###ACTION_DELIMITER###
./hack/quick_install.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y curl
###ACTION_DELIMITER###
./hack/quick_install.sh
###ACTION_DELIMITER###
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && chmod +x ./kubectl && mv ./kubectl /usr/local/bin/kubectl
###ACTION_DELIMITER###
./hack/quick_install.sh
###ACTION_DELIMITER###
curl -LO https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64 && chmod +x kind-linux-amd64 && mv kind-linux-amd64 /usr/local/bin/kind
###ACTION_DELIMITER###
kind create cluster
###ACTION_DELIMITER###
wget https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.14.0/kubebuilder_3.14.0_linux_amd64.tar.gz && tar -zxvf kubebuilder_3.14.0_linux_amd64.tar.gz && mv kubebuilder_3.14.0_linux_amd64 /usr/local/kubebuilder && export KUBEBUILDER_ASSETS=/usr/local/kubebuilder/bin
###ACTION_DELIMITER###
wget https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.13.0/kubebuilder_3.13.0_linux_amd64.tar.gz && tar -zxvf kubebuilder_3.13.0_linux_amd64.tar.gz && mv kubebuilder_3.13.0_linux_amd64 /usr/local/kubebuilder && export KUBEBUILDER_ASSETS=/usr/local/kubebuilder/bin
###ACTION_DELIMITER###
curl -L -o kubebuilder https://go.kubebuilder.io/dl/latest/$(go env GOOS)/$(go env GOARCH) && chmod +x kubebuilder && mv kubebuilder /usr/local/bin/
###ACTION_DELIMITER###
kubebuilder version && export KUBEBUILDER_ASSETS=$(kubebuilder env assets) && go test -v ./pkg/... ./cmd/... -coverprofile coverage.out
###ACTION_DELIMITER###
wget https://github.com/kubernetes-sigs/kubebuilder/releases/download/v2.3.1/kubebuilder_2.3.1_linux_amd64.tar.gz && tar -zxvf kubebuilder_2.3.1_linux_amd64.tar.gz && mv kubebuilder_2.3.1_linux_amd64 /usr/local/kubebuilder && export KUBEBUILDER_ASSETS=/usr/local/kubebuilder/bin && go test -v ./pkg/... ./cmd/... -coverprofile coverage.out
###ACTION_DELIMITER###
echo 'go test -v ./pkg/... ./cmd/... -coverprofile coverage.out' > /home/kserve/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
go test -v ./pkg/... ./cmd/... -coverprofile coverage.out

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
go test -v ./pkg/... ./cmd/... -coverprofile coverage.out

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
go test -v ./pkg/... ./cmd/... -coverprofile coverage.out

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

# Choose an appropriate base image based on the project's requirements - replace [base image] with actual base image
# For example: FROM ubuntu:**, FROM python:**, FROM node:**, FROM centos:**, etc.
FROM python:3.9-slim

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


@Instance.register("kserve", "kserve_1281_to_901")
class KSERVE_1281_TO_901(Instance):
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
        # Implement log parsing logic using regex
        # Extract passed tests
        passed_matches = re.findall(r'--- PASS: (\S+)', log)
        passed_tests.update(passed_matches)
        # Extract failed tests
        failed_matches = re.findall(r'--- FAIL: (\S+)', log)
        failed_tests.update(failed_matches)
        # Extract skipped tests
        skipped_matches = re.findall(r'--- SKIP: (\S+)', log)
        skipped_tests.update(skipped_matches)
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
