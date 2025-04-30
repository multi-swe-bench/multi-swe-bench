#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout fffc4eed8425b518a3bfd11d7b401632b6d8eda0
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

