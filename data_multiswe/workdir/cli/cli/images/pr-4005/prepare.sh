#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 95a515ecf0d9cd006b525074633dce7af3bdfb76
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

