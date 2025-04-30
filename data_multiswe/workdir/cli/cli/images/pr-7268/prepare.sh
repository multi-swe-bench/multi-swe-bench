#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout de07febc26e19000f8c9e821207f3bc34a3c8038
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

