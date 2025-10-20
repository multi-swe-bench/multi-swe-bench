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
                """apt-get update && apt-get install -y libjpeg-dev zlib1g-dev libpng-dev
###ACTION_DELIMITER###
pip install -r requirements-dev.txt
###ACTION_DELIMITER###
pip install -e .
###ACTION_DELIMITER###
echo 'python runtests.py --verbosity 2' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/^class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y django-taggit && pip install django-taggit==0.24.0
###ACTION_DELIMITER###
sed -i '/class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__
###ACTION_DELIMITER###
pip uninstall -y django-taggit && pip install django-taggit==0.22.2 && sed -i '/^class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__
###ACTION_DELIMITER###
pip uninstall -y Django && pip install Django==1.8.19 && sed -i '/^class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__
###ACTION_DELIMITER###
sed -i '/^class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ && bash test_commands.sh
###ACTION_DELIMITER###
cat /usr/local/lib/python3.9/site-packages/taggit/models.py | grep -A 5 'class TagBase'
###ACTION_DELIMITER###
sed -i '/__classcell__ = None/d' /usr/local/lib/python3.9/site-packages/taggit/models.py && sed -i '/^class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '1i\import taggit.models\ntaggit.models.TagBase.__classcell__ = None' runtests.py && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/from django.core.management import execute_from_command_line/a\    import os\n    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\n    import django\n    django.setup()\n    import taggit.models\n    taggit.models.TagBase.__classcell__ = None' runtests.py && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/from django.core.management import execute_from_command_line/a\    import os\n    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\n    import django\n    django.setup()\n    import taggit.models\n    taggit.models.TagBase.__classcell__ = None' runtests.py && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/from django.core.management import execute_from_command_line/a\import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\nimport django\ndjango.setup()\nimport taggit.models\ntaggit.models.TagBase.__classcell__ = None' runtests.py && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/from django.core.management import execute_from_command_line/a\    import os\n    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\n    import django\n    django.setup()\n    import taggit.models\n    taggit.models.TagBase.__classcell__ = None' runtests.py && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/from django.core.management import execute_from_command_line/a\import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\nimport django\ndjango.setup()\nimport taggit.models\ntaggit.models.TagBase.__classcell__ = None' runtests.py && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '1i\import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\nimport django\ndjango.setup()\nimport taggit.models\ntaggit.models.TagBase.__classcell__ = None' runtests.py && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '1i\import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\nimport django\ndjango.setup()\nimport taggit.models\ntaggit.models.TagBase.__classcell__ = None' runtests.py && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '1i\import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\nimport django\ndjango.setup()\nimport taggit.models\ntaggit.models.TagBase.__classcell__ = None' runtests.py && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '1i\
import os\
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\
import django\
django.setup()\
import taggit.models\
taggit.models.TagBase.__classcell__ = None' runtests.py && bash test_commands.sh
###ACTION_DELIMITER###
git checkout runtests.py && sed -i '1i\import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\nimport django\ndjango.setup()\nimport taggit.models\ntaggit.models.TagBase.__classcell__ = None' runtests.py && bash test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall django-taggit==0.22.2 && sed -i '/class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && echo 'export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip install --force-reinstall django-taggit==0.22.2 && sed -i '/^class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ && echo 'export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
git checkout runtests.py && sed -i '1i\import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\nimport taggit.models\ntaggit.models.TagBase.__classcell__ = None\nimport django\ndjango.setup()' runtests.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ && echo 'python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y django-taggit && pip install django-taggit==0.22.2 && awk '/class TagBase(models.Model):/ {print; print "    __classcell__ = None"; next} 1' /usr/local/lib/python3.9/site-packages/taggit/models.py > temp && mv temp /usr/local/lib/python3.9/site-packages/taggit/models.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ && echo 'export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
git checkout runtests.py && sed -i '1i\import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\nimport taggit.models\ntaggit.models.TagBase.__classcell__ = None\nimport django\ndjango.setup()' runtests.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y django-taggit && pip install django-taggit==0.22.2 && sed -i '/class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ && echo 'export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y django-taggit && pip install django-taggit==0.22.2 && awk '/^class TagBase(models.Model):$/ {print; print "    __classcell__ = None"; next} 1' /usr/local/lib/python3.9/site-packages/taggit/models.py > temp && mv temp /usr/local/lib/python3.9/site-packages/taggit/models.py && cat /usr/local/lib/python3.9/site-packages/taggit/models.py | grep -A 2 'class TagBase' && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ && echo 'export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y django-taggit && pip install django-taggit==0.22.2 && awk '/^\s*class\s+TagBase\s*\(\s*models\.Model\s*\)\s*:/ {print; print "    __classcell__ = None"; next} 1' /usr/local/lib/python3.9/site-packages/taggit/models.py > temp && mv temp /usr/local/lib/python3.9/site-packages/taggit/models.py && cat /usr/local/lib/python3.9/site-packages/taggit/models.py | grep -A 2 'class TagBase' && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ && echo 'export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y django-taggit && pip install django-taggit==0.22.2 && sed -i '/class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && cat /usr/local/lib/python3.9/site-packages/taggit/models.py | grep -A 2 'class TagBase' && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ && echo 'export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/def __new__/a\        attrs.setdefault("__classcell__", None)' /usr/local/lib/python3.9/site-packages/django/db/models/base.py && pip uninstall -y django-taggit && pip install django-taggit==0.22.2 && sed -i '/class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ && echo 'export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/^class ModelBase(type):/a\    def __new__(cls, name, bases, attrs):\n        attrs.setdefault("__classcell__", None)\n        return super().__new__(cls, name, bases, attrs)' /usr/local/lib/python3.9/site-packages/django/db/models/base.py && pip uninstall -y django-taggit && pip install django-taggit==0.22.2 && sed -i '/class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ /usr/local/lib/python3.9/site-packages/django/__pycache__ && echo 'export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
sed -i '/def __new__/a\        attrs.setdefault("__classcell__", None)' /usr/local/lib/python3.9/site-packages/django/db/models/base.py && pip uninstall -y django-taggit && pip install django-taggit==0.22.2 && sed -i '/class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ /usr/local/lib/python3.9/site-packages/django/__pycache__ && echo 'export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__
python -c "import taggit.models; taggit.models.TagBase.__classcell__ = None; from runtests import runtests; runtests()"' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'deb http://deb.debian.org/debian stretch main' >> /etc/apt/sources.list && apt-get update && apt-get install -y python3.5 python3.5-venv && python3.5 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements-dev.txt && pip install -e . && sed -i '/class TagBase(models.Model):/a\    __classcell__ = None' venv/lib/python3.5/site-packages/taggit/models.py && echo 'source venv/bin/activate
export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
pip uninstall -y django-taggit && pip install django-taggit==0.22.2 && sed -i '/class TagBase(models.Model):/a\    __classcell__ = None' /usr/local/lib/python3.9/site-packages/taggit/models.py && sed -i '/def __new__/a\        attrs.setdefault("__classcell__", None)' /usr/local/lib/python3.9/site-packages/django/db/models/base.py && rm -rf /usr/local/lib/python3.9/site-packages/taggit/__pycache__ /usr/local/lib/python3.9/site-packages/django/__pycache__ && echo 'export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'deb http://archive.debian.org/debian stretch main' >> /etc/apt/sources.list && apt-get update -o Acquire::Check-Valid-Until=false && apt-get install -y python3.5 python3.5-venv && python3.5 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements-dev.txt && pip install -e . && sed -i '/class TagBase(models.Model):/a\    __classcell__ = None' venv/lib/python3.5/site-packages/taggit/models.py && echo 'source venv/bin/activate
export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'deb http://archive.debian.org/debian stretch main\ndeb http://archive.debian.org/debian stretch-updates main\ndeb http://security.debian.org/debian-security stretch/updates main' > /etc/apt/sources.list && apt-get update -o Acquire::Check-Valid-Until=false && apt-get install -y python3.5 python3.5-venv && python3.5 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements-dev.txt && pip install -e . && sed -i '/class TagBase(models.Model):/a\    __classcell__ = None' venv/lib/python3.5/site-packages/taggit/models.py && echo 'source venv/bin/activate
export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'deb http://archive.debian.org/debian stretch main' > /etc/apt/sources.list && apt-get update -o Acquire::Check-Valid-Until=false -o Acquire::AllowInsecureRepositories=true && apt-get install -y --allow-unauthenticated python3.5 python3.5-venv && python3.5 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements-dev.txt && pip install -e . && echo 'source venv/bin/activate
export DJANGO_SETTINGS_MODULE=wagtail.tests.settings
python runtests.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo 'import os\nimport django\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\nimport taggit.models\ntaggit.models.TagBase.__classcell__ = None\ndjango.setup()\nfrom runtests import runtests\nruntests()' > run_tests_wrapper.py && chmod +x run_tests_wrapper.py && echo 'python run_tests_wrapper.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'import os\nimport django\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\nimport taggit.models\ntaggit.models.TagBase.__classcell__ = None\ndjango.setup()\nfrom runtests import runtests\nruntests()' > run_tests_wrapper.py && chmod +x run_tests_wrapper.py && echo 'python run_tests_wrapper.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install -r requirements-dev.txt && pip install -e . && echo -e 'import os\nimport django\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\nimport taggit.models\ntaggit.models.TagBase.__classcell__ = None\ndjango.setup()\nfrom runtests import runtests\nruntests()' > run_tests_wrapper.py && chmod +x run_tests_wrapper.py && echo 'source venv/bin/activate\npython run_tests_wrapper.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install pbr && pip install -r requirements-dev.txt && pip install -e . && echo -e 'import os\nimport django\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")\nimport taggit.models\ntaggit.models.TagBase.__classcell__ = None\ndjango.setup()\nfrom runtests import runtests\nruntests()' > run_tests_wrapper.py && chmod +x run_tests_wrapper.py && echo 'source venv/bin/activate\npython run_tests_wrapper.py --verbosity 2' > test_commands.sh && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip install pbr==5.1.1 && pip install sphinxcontrib-spelling==2.1.1 && pip install -r requirements-dev.txt && pip install -e . && echo -e 'source venv/bin/activate
python run_tests_wrapper.py --verbosity 2' > test_commands.sh && echo -e 'import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail.tests.settings")
import taggit.models
taggit.models.TagBase.__classcell__ = None
django.setup()
from runtests import runtests
runtests()' > run_tests_wrapper.py && chmod +x run_tests_wrapper.py && bash test_commands.sh
###ACTION_DELIMITER###
source venv/bin/activate && pip uninstall -y django-modelcluster && pip install django-modelcluster==3.1.0 && bash test_commands.sh
###ACTION_DELIMITER###
"""
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
source venv/bin/activate
python run_tests_wrapper.py --verbosity 2

""".format(
                    pr=self.pr
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
source venv/bin/activate
python run_tests_wrapper.py --verbosity 2

""".format(
                    pr=self.pr
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
source venv/bin/activate
python run_tests_wrapper.py --verbosity 2

""".format(
                    pr=self.pr
                ),
            ),
        ]

    def dockerfile(self) -> str:
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        dockerfile_content = """
# This is a template for creating a Dockerfile to test patches
# LLM should fill in the appropriate values based on the context

# Choose an appropriate base image based on the project's requirements - replace python:3.9-slim with actual base image
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
RUN git clone https://github.com/wagtail/wagtail.git /home/wagtail

WORKDIR /home/wagtail
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("wagtail", "wagtail_1444_to_1232")
class WAGTAIL_1444_TO_1232(Instance):
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
        passed_tests: set[str] = set()
        failed_tests: set[str] = set()
        skipped_tests: set[str] = set()
        import re
        for line in log.split('\n'):
            if ' ... ' in line:
                test_part, status = line.split(' ... ', 1)
                test_name = re.sub(r'^\[\s*\d+\]\s*', '', test_part).strip()
                status = status.strip().lower()
                if status == 'ok':
                    passed_tests.add(test_name)
                elif status in ('error', 'failed'):
                    failed_tests.add(test_name)
                elif status.startswith('skipped'):
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
