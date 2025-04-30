#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 25d79c4e16d54d6f3621517269f07048748a6b97
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

