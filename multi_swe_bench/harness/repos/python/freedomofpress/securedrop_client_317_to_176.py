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
                """apt-get update && apt-get install -y make python3-pyqt5 python3-pyqt5.qtsvg xvfb
###ACTION_DELIMITER###
pip install pipenv
###ACTION_DELIMITER###
sed -i 's/python_version = "3.5"/python_version = "3.9"/' Pipfile
###ACTION_DELIMITER###
rm -f Pipfile.lock
###ACTION_DELIMITER###
pipenv lock
###ACTION_DELIMITER###
pipenv sync --dev
###ACTION_DELIMITER###
echo 'pipenv run make check' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
cat Makefile
###ACTION_DELIMITER###
echo 'pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get update && apt-get install -y gnupg sqlite3 libsqlite3-dev
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libxcb-xinerama0 libxcb-randr0 libxcb-xfixes0 libxcb-shape0 libxcb-shm0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-render0 libxcb-xkb1 libxkbcommon-x11-0 libxkbcommon0 libgpgme11
###ACTION_DELIMITER###
echo 'QT_QPA_PLATFORM=offscreen pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
EOF
###ACTION_DELIMITER###
export GPG_TTY=$(tty) && gpg-agent --daemon && gpg --batch --pinentry-mode loopback --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
Passphrase: ''
EOF
###ACTION_DELIMITER###
gpgconf --kill gpg-agent && gpg-agent --daemon --allow-loopback-pinentry && export GPG_TTY=$(tty) && gpg --batch --pinentry-mode loopback --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
Passphrase: ''
EOF
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077
QT_QPA_PLATFORM=offscreen
export GNUPGHOME=$(mktemp -d)
gpg --batch --import /root/.gnupg/pubring.kbx
pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077
QT_QPA_PLATFORM=offscreen
export GNUPGHOME=$(mktemp -d)
gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
Passphrase: ''
EOF
xvfb-run -a pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077
QT_QPA_PLATFORM=offscreen
export GNUPGHOME=$(mktemp -d)
gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
Passphrase:
EOF
xvfb-run -s "-screen 0 1024x768x24" pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077
QT_QPA_PLATFORM=offscreen
export GNUPGHOME=$(mktemp -d)
gpg --batch --passphrase "" --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
EOF
xvfb-run -a pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077
QT_QPA_PLATFORM=offscreen
export GNUPGHOME=$(mktemp -d)
gpg --batch --passphrase "" --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
EOF
xvfb-run -s "-screen 0 1024x768x24" -a pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077
QT_QPA_PLATFORM=offscreen
export GNUPGHOME=$(mktemp -d)
gpg --batch --passphrase "" --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
EOF
xvfb-run -s "-screen 0 1024x768x24" -a pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077
QT_QPA_PLATFORM=offscreen
export GNUPGHOME=$(mktemp -d)
gpg --batch --passphrase "" --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
EOF
xvfb-run -s "-screen 0 1024x768x24" -a pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077
QT_QPA_PLATFORM=offscreen
export GNUPGHOME=$(mktemp -d)
gpg --batch --passphrase "" --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
EOF
xvfb-run -s "-screen 0 1024x768x24" -a pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077
QT_QPA_PLATFORM=offscreen
export GNUPGHOME=$(mktemp -d)
gpg --batch --passphrase "" --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
EOF
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077
QT_QPA_PLATFORM=offscreen
export GNUPGHOME=$(mktemp -d)
gpg --batch --passphrase "" --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
EOF
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077
QT_QPA_PLATFORM=offscreen
export GNUPGHOME=$(mktemp -d)
gpg --batch --passphrase "" --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
EOF
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077
QT_QPA_PLATFORM=offscreen
export GNUPGHOME=$(mktemp -d)
gpg --batch --passphrase "" --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
EOF
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077
QT_QPA_PLATFORM=offscreen
export GNUPGHOME=$(mktemp -d)
gpg --batch --passphrase "" --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
EOF
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077

export GNUPGHOME=$(mktemp -d)
# Generate unprotected GPG key for testing
gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
%no-protection
EOF

# Ensure Xvfb and Qt rendering work
export QT_QPA_PLATFORM=offscreen
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077

export GNUPGHOME=$(mktemp -d)
# Generate unprotected GPG key
 gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
%no-protection
EOF

# Test Xvfb independently
xvfb-run -a -s "-screen 0 1024x768x24" echo "Xvfb test successful"
if [ $? -ne 0 ]; then
  echo "Xvfb failed to start"
  exit 1
fi

# Run tests with Xvfb
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077

# Install missing X11 dependencies
apt-get update && apt-get install -y libx11-xcb1 libxcb1 libxrender1 libxi6 libxext6 libxfixes3 libxdamage1 libxcomposite1 libxrandr2 libxcursor1 libxinerama1

export GNUPGHOME=$(mktemp -d)
# Generate unprotected GPG key
 gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
%no-protection
EOF

# Test Xvfb with logging
xvfb-run -a -s "-screen 0 1024x768x24" -e /tmp/xvfb.log echo "Xvfb test successful"
if [ $? -ne 0 ]; then
  echo "Xvfb failed to start. Logs:"
  cat /tmp/xvfb.log
  exit 1
fi

# Run tests with Xvfb
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run make test' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077

export GNUPGHOME=$(mktemp -d)
# Generate and export GPG key
 gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
%no-protection
EOF
# Export public key for tests
gpg --batch --export -a test@example.com > test_key.asc

# Run tests directly with pytest and Xvfb
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run pytest -v --random-order-bucket=global --cov=securedrop_client tests/' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077

export GNUPGHOME=$(mktemp -d)
# Generate unprotected GPG key and export public key
gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
%no-protection
EOF
gpg --batch --export -a test@example.com > test_key.asc

# Configure headless rendering and run tests with verbose logging
export QT_QPA_PLATFORM=offscreen
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run pytest -v --random-order-bucket=global --cov=securedrop_client tests/' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077

export GNUPGHOME=$(mktemp -d)
# Generate and export GPG key
gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
%no-protection
EOF
gpg --batch --export -a test@example.com > test_key.asc

# Run tests with Xvfb logging
export QT_QPA_PLATFORM=offscreen
xvfb-run -a -s "-screen 0 1024x768x24" -e /tmp/xvfb_test.log pipenv run pytest -v --random-order-bucket=global --cov=securedrop_client tests/
# Check if Xvfb failed and log details
if [ $? -ne 0 ]; then
  echo "Tests failed. Xvfb logs:"
  cat /tmp/xvfb_test.log
fi' > test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077

export GNUPGHOME=$(mktemp -d)
# Generate and export GPG key
gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
%no-protection
EOF
gpg --batch --export -a test@example.com > test_key.asc
# Import key into test keyring
gpg --batch --import test_key.asc

# Debug: Check GPG key availability
echo "GPG public keys available:"
gpg --list-keys

# Configure headless rendering
export QT_QPA_PLATFORM=offscreen
# Debug: Check environment variables
echo "Environment variables:"
env | grep -E "DISPLAY|QT_|GNUPGHOME"

# Run tests with Xvfb and detailed logging
xvfb-run -a -s "-screen 0 1024x768x24" -e /tmp/xvfb_test.log pipenv run pytest -v tests/

# Capture and display Xvfb logs if tests fail
if [ $? -ne 0 ]; then
  echo "Tests failed. Xvfb logs:"
  cat /tmp/xvfb_test.log
  exit 1
fi' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077

export GNUPGHOME=$(mktemp -d)
# Generate and import GPG key
gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
%no-protection
EOF
gpg --batch --export -a test@example.com > test_key.asc
gpg --batch --import test_key.asc

# Ensure GPG key is visible to tests
echo "GPG keyring contents:"
gpg --list-keys

# Configure headless rendering and disable coverage to reduce complexity
export QT_QPA_PLATFORM=offscreen
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run pytest -v -p no:cov tests/

# Capture core dump if segmentation fault occurs
if [ $? -eq 139 ]; then
  echo "Segmentation fault detected. Check core dump."
  exit 1
fi' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'umask 0077

# Update dependencies and install PyQt5 explicitly
pipenv install pyqt5==5.15.6

# Generate and import GPG key into user keyring
gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
%no-protection
EOF
gpg --batch --export -a test@example.com > test_key.asc
gpg --batch --import test_key.asc

# Configure headless rendering and run tests with debug logging
export QT_QPA_PLATFORM=offscreen
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run pytest -v --full-trace tests/' > test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
umask 0077

# Update dependencies and install PyQt5 explicitly
pipenv install pyqt5==5.15.6

# Generate and import GPG key into user keyring
gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
%no-protection
EOF
gpg --batch --export -a test@example.com > test_key.asc
gpg --batch --import test_key.asc

# Configure headless rendering and run tests with debug logging
export QT_QPA_PLATFORM=offscreen
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run pytest -v --full-trace tests/

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
umask 0077

# Update dependencies and install PyQt5 explicitly
pipenv install pyqt5==5.15.6

# Generate and import GPG key into user keyring
gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
%no-protection
EOF
gpg --batch --export -a test@example.com > test_key.asc
gpg --batch --import test_key.asc

# Configure headless rendering and run tests with debug logging
export QT_QPA_PLATFORM=offscreen
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run pytest -v --full-trace tests/

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
umask 0077

# Update dependencies and install PyQt5 explicitly
pipenv install pyqt5==5.15.6

# Generate and import GPG key into user keyring
gpg --batch --gen-key <<EOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 0
%no-protection
EOF
gpg --batch --export -a test@example.com > test_key.asc
gpg --batch --import test_key.asc

# Configure headless rendering and run tests with debug logging
export QT_QPA_PLATFORM=offscreen
xvfb-run -a -s "-screen 0 1024x768x24" pipenv run pytest -v --full-trace tests/

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
RUN git clone https://github.com/freedomofpress/securedrop-client.git /home/securedrop-client

WORKDIR /home/securedrop-client
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("freedomofpress", "securedrop_client_317_to_176")
class SECUREDROP_CLIENT_317_TO_176(Instance):
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
        passed_tests = set[str]()
        failed_tests = set[str]()
        skipped_tests = set[str]()
        import re
        import json
        # Extract all test names using the pattern tests/...::... (stop at first whitespace)
        all_tests = set(re.findall(r'tests/[^:]+::\S+', log))
        # Extract failed tests (stop at first whitespace)
        failed_matches = re.findall(r'FAILED (tests/[^:]+::\S+)', log)
        failed_tests = set(failed_matches)
        # Extract skipped tests (stop at first whitespace)
        skipped_matches = re.findall(r'SKIPPED (tests/[^:]+::\S+)', log)
        skipped_tests = set(skipped_matches)
        # Calculate passed tests as all tests minus failed and skipped
        passed_tests = all_tests - failed_tests - skipped_tests
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
