#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 02881b4783db05be2249c27f36130e3ef82daa9a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

