#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 34d549e7b61660c7c993181c0be046d6277cad03
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

