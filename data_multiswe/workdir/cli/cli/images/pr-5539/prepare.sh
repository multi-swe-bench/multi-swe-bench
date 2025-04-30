#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout beba0e1d78996f0033c77e462e6bf9db0fecc2af
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

