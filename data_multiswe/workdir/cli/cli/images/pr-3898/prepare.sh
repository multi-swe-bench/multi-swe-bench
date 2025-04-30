#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout c3e6fccabe699aaac46bafcc2317d36a0a727969
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

