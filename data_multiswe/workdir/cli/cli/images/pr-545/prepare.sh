#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 7950023a8775066fcf2c5552e2cd6ec582ceb34e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

