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
        repo_name = self.pr.repo
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
venv/bin/pip install -e ./opentelemetry-api -e ./opentelemetry-sdk
###ACTION_DELIMITER###
python3.9 -m venv venv
###ACTION_DELIMITER###
apt-get update && apt-get install -y software-properties-common
###ACTION_DELIMITER###
add-apt-repository ppa:deadsnakes/ppa -y && apt-get update
###ACTION_DELIMITER###
apt-get install -y python3.9 python3.9-venv python3.9-dev
###ACTION_DELIMITER###
python3.9 -m venv venv
###ACTION_DELIMITER###
venv/bin/pip install -r dev-requirements.txt
###ACTION_DELIMITER###
venv/bin/pip install -e ./opentelemetry-api -e ./opentelemetry-sdk
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
apt-get install -y libpq-dev default-libmysqlclient-dev libssl-dev libsqlite3-dev
###ACTION_DELIMITER###
for ext in ext/opentelemetry-ext-*; do venv/bin/pip install -e $ext; done
###ACTION_DELIMITER###
for ext in ext/opentelemetry-ext-*; do if [[ $ext != *"docker-tests"* ]]; then venv/bin/pip install -e $ext; fi; done
###ACTION_DELIMITER###
venv/bin/pip install -e ./opentelemetry-auto-instrumentation
###ACTION_DELIMITER###
venv/bin/pip install -e ./ext/opentelemetry-ext-wsgi && venv/bin/pip install -e ./ext/opentelemetry-ext-flask
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider ./...' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/ ext/' > test_commands.sh
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider' > test_commands.sh
###ACTION_DELIMITER###
apt-get install -y python3.8 python3.8-venv python3.8-dev
###ACTION_DELIMITER###
python3.8 -m venv venv
###ACTION_DELIMITER###
venv/bin/pip install -r dev-requirements.txt
###ACTION_DELIMITER###
venv/bin/pip install -e ./opentelemetry-api -e ./opentelemetry-sdk && for ext in ext/opentelemetry-ext-*; do if [[ $ext != *"docker-tests"* ]]; then venv/bin/pip install -e $ext; fi; done
###ACTION_DELIMITER###
venv/bin/pip install -e ./opentelemetry-auto-instrumentation -e ./ext/opentelemetry-ext-wsgi && venv/bin/pip install -e ./ext/opentelemetry-ext-flask
###ACTION_DELIMITER###
echo 'venv/bin/pytest -v --no-header -rA --tb=no -p no:cacheprovider tests/ opentelemetry-api/tests/ opentelemetry-sdk/tests/ opentelemetry-auto-instrumentation/tests/ ext/*/tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'venv/bin/pytest --rootdir=. -v --no-header -rA --tb=no -p no:cacheprovider tests/ opentelemetry-api/tests/ opentelemetry-sdk/tests/ opentelemetry-auto-instrumentation/tests/ ext/*/tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONPATH=. venv/bin/pytest --rootdir=. -v --no-header -rA --tb=no -p no:cacheprovider tests/ opentelemetry-api/tests/ opentelemetry-sdk/tests/ opentelemetry-auto-instrumentation/tests/ ext/*/tests/' > test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider tests/ opentelemetry-api/tests/ opentelemetry-sdk/tests/ opentelemetry-auto-instrumentation/tests/ ext/*/tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-api/tests/ opentelemetry-sdk/tests/ opentelemetry-auto-instrumentation/tests/ ext/opentelemetry-ext-flask/tests/ ext/opentelemetry-ext-dbapi/tests/ ext/opentelemetry-ext-grpc/tests/ ext/opentelemetry-ext-http-requests/tests/ ext/opentelemetry-ext-jaeger/tests/ ext/opentelemetry-ext-mysql/tests/ ext/opentelemetry-ext-otcollector/tests/ ext/opentelemetry-ext-prometheus/tests/ ext/opentelemetry-ext-psycopg2/tests/ ext/opentelemetry-ext-pymongo/tests/ ext/opentelemetry-ext-pymysql/tests/ ext/opentelemetry-ext-redis/tests/ ext/opentelemetry-ext-sqlalchemy/tests/ ext/opentelemetry-ext-wsgi/tests/ ext/opentelemetry-ext-zipkin/tests/' > test_commands.sh
###ACTION_DELIMITER###
echo 'PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=append -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-api/tests/ opentelemetry-sdk/tests/ opentelemetry-auto-instrumentation/tests/ ext/opentelemetry-ext-flask/tests/ ext/opentelemetry-ext-dbapi/tests/ ext/opentelemetry-ext-grpc/tests/ ext/opentelemetry-ext-http-requests/tests/ ext/opentelemetry-ext-jaeger/tests/ ext/opentelemetry-ext-mysql/tests/ ext/opentelemetry-ext-otcollector/tests/ ext/opentelemetry-ext-prometheus/tests/ ext/opentelemetry-ext-psycopg2/tests/ ext/opentelemetry-ext-pymongo/tests/ ext/opentelemetry-ext-pymysql/tests/ ext/opentelemetry-ext-redis/tests/ ext/opentelemetry-ext-sqlalchemy/tests/ ext/opentelemetry-ext-wsgi/tests/ ext/opentelemetry-ext-zipkin/tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo 'venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-api/tests/ opentelemetry-sdk/tests/ opentelemetry-auto-instrumentation/tests/ ext/opentelemetry-ext-flask/tests/ ext/opentelemetry-ext-dbapi/tests/ ext/opentelemetry-ext-grpc/tests/ ext/opentelemetry-ext-http-requests/tests/ ext/opentelemetry-ext-jaeger/tests/ ext/opentelemetry-ext-mysql/tests/ ext/opentelemetry-ext-otcollector/tests/ ext/opentelemetry-ext-prometheus/tests/ ext/opentelemetry-ext-psycopg2/tests/ ext/opentelemetry-ext-pymongo/tests/ ext/opentelemetry-ext-pymysql/tests/ ext/opentelemetry-ext-redis/tests/ ext/opentelemetry-ext-sqlalchemy/tests/ ext/opentelemetry-ext-wsgi/tests/ ext/opentelemetry-ext-zipkin/tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-api/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-sdk/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-auto-instrumentation/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-flask/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-dbapi/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-grpc/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-http-requests/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-jaeger/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-mysql/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-otcollector/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-prometheus/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-psycopg2/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymongo/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymysql/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-redis/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-sqlalchemy/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-wsgi/tests/
venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-zipkin/tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###
echo -e 'PYTHONPATH=opentelemetry-api/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-api/tests/
PYTHONPATH=opentelemetry-sdk/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-sdk/tests/
PYTHONPATH=opentelemetry-auto-instrumentation/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-auto-instrumentation/tests/
PYTHONPATH=ext/opentelemetry-ext-flask/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-flask/tests/
PYTHONPATH=ext/opentelemetry-ext-dbapi/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-dbapi/tests/
PYTHONPATH=ext/opentelemetry-ext-grpc/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-grpc/tests/
PYTHONPATH=ext/opentelemetry-ext-http-requests/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-http-requests/tests/
PYTHONPATH=ext/opentelemetry-ext-jaeger/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-jaeger/tests/
PYTHONPATH=ext/opentelemetry-ext-mysql/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-mysql/tests/
PYTHONPATH=ext/opentelemetry-ext-otcollector/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-otcollector/tests/
PYTHONPATH=ext/opentelemetry-ext-prometheus/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-prometheus/tests/
PYTHONPATH=ext/opentelemetry-ext-psycopg2/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-psycopg2/tests/
PYTHONPATH=ext/opentelemetry-ext-pymongo/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymongo/tests/
PYTHONPATH=ext/opentelemetry-ext-pymysql/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymysql/tests/
PYTHONPATH=ext/opentelemetry-ext-redis/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-redis/tests/
PYTHONPATH=ext/opentelemetry-ext-sqlalchemy/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-sqlalchemy/tests/
PYTHONPATH=ext/opentelemetry-ext-wsgi/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-wsgi/tests/
PYTHONPATH=ext/opentelemetry-ext-zipkin/tests/ venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-zipkin/tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-api/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-sdk/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-auto-instrumentation/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-flask/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-dbapi/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-grpc/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-http-requests/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-jaeger/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-mysql/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-otcollector/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-prometheus/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-psycopg2/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymongo/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymysql/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-redis/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-sqlalchemy/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-wsgi/tests/
PYTHONPATH=. venv/bin/pytest --rootdir=. --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-zipkin/tests/' > test_commands.sh
###ACTION_DELIMITER###
echo -e 'PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-api/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-sdk/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-auto-instrumentation/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-flask/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-dbapi/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-grpc/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-http-requests/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-jaeger/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-mysql/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-otcollector/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-prometheus/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-psycopg2/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymongo/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymysql/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-redis/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-sqlalchemy/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-wsgi/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-zipkin/tests/' > test_commands.sh
###ACTION_DELIMITER###
bash test_commands.sh
###ACTION_DELIMITER###

###ACTION_DELIMITER###
venv/bin/pip install sqlalchemy
###ACTION_DELIMITER###
""",
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
cd /home/[[REPO_NAME]]
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-api/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-sdk/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-auto-instrumentation/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-flask/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-dbapi/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-grpc/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-http-requests/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-jaeger/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-mysql/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-otcollector/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-prometheus/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-psycopg2/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymongo/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymysql/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-redis/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-sqlalchemy/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-wsgi/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-zipkin/tests/

""".replace("[[REPO_NAME]]", repo_name),
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
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-api/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-sdk/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-auto-instrumentation/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-flask/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-dbapi/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-grpc/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-http-requests/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-jaeger/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-mysql/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-otcollector/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-prometheus/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-psycopg2/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymongo/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymysql/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-redis/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-sqlalchemy/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-wsgi/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-zipkin/tests/

""".replace("[[REPO_NAME]]", repo_name),
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
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-api/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-sdk/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider opentelemetry-auto-instrumentation/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-flask/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-dbapi/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-grpc/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-http-requests/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-jaeger/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-mysql/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-otcollector/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-prometheus/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-psycopg2/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymongo/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-pymysql/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-redis/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-sqlalchemy/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-wsgi/tests/
PYTHONPATH=. venv/bin/pytest --import-mode=importlib -v --no-header -rA --tb=no -p no:cacheprovider ext/opentelemetry-ext-zipkin/tests/

""".replace("[[REPO_NAME]]", repo_name),
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
RUN git clone https://github.com/open-telemetry/opentelemetry-python.git /home/opentelemetry-python

WORKDIR /home/opentelemetry-python
RUN git reset --hard
RUN git checkout {pr.base.sha}
"""
        dockerfile_content += f"""
{copy_commands}
"""
        return dockerfile_content.format(pr=self.pr)


@Instance.register("open-telemetry", "opentelemetry_python_567_to_340")
class OPENTELEMETRY_PYTHON_567_TO_340(Instance):
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

        return "bash /home/run.sh"

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

        # Regex pattern to match test lines with status (PASSED, FAILED, SKIPPED, etc.)
        pattern = re.compile(
            r"^(.+?)\s+(PASSED|FAILED|SKIPPED|XFAIL|ERROR)\s+\[\s*\d+%\]$"
        )
        for line in log.split("\n"):
            line = line.strip()
            match = pattern.match(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
                if status == "PASSED":
                    passed_tests.add(test_name)
                elif status == "FAILED":
                    failed_tests.add(test_name)
                elif status == "SKIPPED":
                    skipped_tests.add(test_name)
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
