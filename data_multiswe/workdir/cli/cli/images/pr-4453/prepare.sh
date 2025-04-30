#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 0c5c2378ac540f07700dd87b55bbb3313a728ca2
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

