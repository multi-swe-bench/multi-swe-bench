#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 78ac77180e833acaf233fb252d4c8e232800d603
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

