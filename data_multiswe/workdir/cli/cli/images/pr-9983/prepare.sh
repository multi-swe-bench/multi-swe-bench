#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 9983939d534ffe66ca0a67abb00c2af892f5c495
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

