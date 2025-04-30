#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 255f5301d50176f9db4acdefb76eaf79ed598242
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

