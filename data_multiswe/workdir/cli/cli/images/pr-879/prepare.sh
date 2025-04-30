#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 4ef468c19a0d946d67bab383ad94356d271d7c2d
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

