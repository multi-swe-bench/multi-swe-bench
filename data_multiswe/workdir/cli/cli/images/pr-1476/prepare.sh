#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 0cc59488a80c56f69be17dfe98ff76334f618a7e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

