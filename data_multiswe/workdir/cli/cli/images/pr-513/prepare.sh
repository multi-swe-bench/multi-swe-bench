#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout cc96ddd5514c04ee90fff11c840aad68af9fada3
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

