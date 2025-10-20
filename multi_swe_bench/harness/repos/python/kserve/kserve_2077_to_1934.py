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
        return "ubuntu:22.04"
    
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
go version
###ACTION_DELIMITER###
apt-get update
###ACTION_DELIMITER###
apt-get install -y golang-go
###ACTION_DELIMITER###
go version
###ACTION_DELIMITER###
go mod download
###ACTION_DELIMITER###
go install sigs.k8s.io/controller-runtime/tools/setup-envtest@latest
###ACTION_DELIMITER###
go install sigs.k8s.io/controller-runtime/tools/setup-envtest@v0.0.0-20221004135044-701f0a163409
###ACTION_DELIMITER###
go install sigs.k8s.io/controller-runtime/tools/setup-envtest@v0.10.2
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
apt-get install -y make
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
go install sigs.k8s.io/controller-tools/cmd/controller-gen@v0.4.0 && mkdir -p /home/kserve/bin && cp $(go env GOPATH)/bin/controller-gen /home/kserve/bin/
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
apt-get install -y yq
###ACTION_DELIMITER###
go install github.com/mikefarah/yq/v3@latest && cp $(go env GOPATH)/bin/yq /usr/local/bin/
###ACTION_DELIMITER###
yq --version
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
go install sigs.k8s.io/kustomize/kustomize/v4@latest && cp $(go env GOPATH)/bin/kustomize /home/kserve/bin/
###ACTION_DELIMITER###
kustomize version
###ACTION_DELIMITER###
go install sigs.k8s.io/kustomize/kustomize/v4@latest && cp $(go env GOPATH)/bin/kustomize /usr/local/bin/
###ACTION_DELIMITER###
ls /usr/local/bin
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
apt-get install -y etcd
###ACTION_DELIMITER###
make test
###ACTION_DELIMITER###
go install sigs.k8s.io/controller-runtime/tools/setup-envtest@v0.0.0-20220502171332-7f0198f53b6e && setup-envtest use 1.22 -p path
###ACTION_DELIMITER###
wget https://storage.googleapis.com/kubebuilder-tools/kubebuilder-tools-1.22.0-linux-amd64.tar.gz && tar -xvf kubebuilder-tools-1.22.0-linux-amd64.tar.gz && export KUBEBUILDER_ASSETS=$(pwd)/kubebuilder/bin
###ACTION_DELIMITER###
apt-get install -y wget
###ACTION_DELIMITER###
wget https://storage.googleapis.com/kubebuilder-tools/kubebuilder-tools-1.22.0-linux-amd64.tar.gz && tar -xvf kubebuilder-tools-1.22.0-linux-amd64.tar.gz && export KUBEBUILDER_ASSETS=$(pwd)/kubebuilder/bin
###ACTION_DELIMITER###
export KUBEBUILDER_ASSETS=$(pwd)/kubebuilder/bin && make test
###ACTION_DELIMITER###
ls kubebuilder/bin
###ACTION_DELIMITER###
export KUBEBUILDER_ASSETS=/home/kserve/kubebuilder/bin && make test
###ACTION_DELIMITER###
export PATH=$(go env GOPATH)/bin:$PATH && go install sigs.k8s.io/controller-runtime/tools/setup-envtest@latest && setup-envtest use 1.22 -p path && make test
###ACTION_DELIMITER###
export PATH=$(go env GOPATH)/bin:$PATH && go install sigs.k8s.io/controller-runtime/tools/setup-envtest@v0.14.0 && setup-envtest use 1.22 -p path && make test
###ACTION_DELIMITER###
export KUBEBUILDER_ASSETS=/home/kserve/kubebuilder/bin && export PATH=$KUBEBUILDER_ASSETS:$PATH && make test
###ACTION_DELIMITER###
export PATH=$(go env GOPATH)/bin:$PATH && go install sigs.k8s.io/controller-runtime/tools/setup-envtest@v0.10.2 && setup-envtest use 1.22 -p path && make test
###ACTION_DELIMITER###
echo -e '#!/bin/bash
export KUBEBUILDER_ASSETS=/home/kserve/kubebuilder/bin
make test' > /home/kserve/test_commands.sh && chmod +x /home/kserve/test_commands.sh"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
#!/bin/bash
export KUBEBUILDER_ASSETS=/home/kserve/kubebuilder/bin
make test

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
#!/bin/bash
export KUBEBUILDER_ASSETS=/home/kserve/kubebuilder/bin
make test

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
#!/bin/bash
export KUBEBUILDER_ASSETS=/home/kserve/kubebuilder/bin
make test

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
FROM ubuntu:22.04

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


@Instance.register("kserve", "kserve_2077_to_1934")
class KSERVE_2077_TO_1934(Instance):
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
        passed_tests = set[str]()  # Tests that passed successfully
        failed_tests = set[str]()  # Tests that failed
        skipped_tests = set[str]()  # Tests that were skipped
        import re
        # Parse passed tests
        passed_pattern = re.compile(r'^ok\s+([^\s]+)', re.MULTILINE)
        passed_tests.update(passed_pattern.findall(log))
        # Parse skipped tests
        skipped_pattern = re.compile(r'^\?\s+([^\s]+)\s+\[no test files\]', re.MULTILINE)
        skipped_tests.update(skipped_pattern.findall(log))
        # Parse failed tests (vet errors)
        failed_pattern = re.compile(r'vet:\s+((?:pkg|cmd)/[^/]+/[^/]+)/[^/]+\.go', re.MULTILINE)
        for match in failed_pattern.findall(log):
            package_name = f"github.com/kserve/kserve/{match}"
            failed_tests.add(package_name)
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
