#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout de5c59aad38eb28eb3328b8845ad61c820b3fbc8
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

