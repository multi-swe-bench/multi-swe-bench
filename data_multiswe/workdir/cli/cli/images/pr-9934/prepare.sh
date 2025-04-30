#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 4c8d124d370f9f58d9a8d8d5a5b590f409542bbe
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

