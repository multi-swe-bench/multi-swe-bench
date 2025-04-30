#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout fef41950044330365f4ce6cbdd77ad3ea406922f
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

