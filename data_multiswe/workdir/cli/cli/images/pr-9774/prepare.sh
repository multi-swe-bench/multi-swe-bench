#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 8b0b0ce1843fcdcf662e655ddc05a1e10fd4a747
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

