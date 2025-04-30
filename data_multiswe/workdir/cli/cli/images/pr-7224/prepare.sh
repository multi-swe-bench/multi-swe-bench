#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 82927b0cc2a831adda22b0a7bf43938bd15e1126
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

