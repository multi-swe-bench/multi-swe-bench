#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e4ce0d76aac90a0c56365777d87d5e458104170e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

