#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout ca7a9364fd56bfa9e33d60e459eb9c1ad91511b9
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

