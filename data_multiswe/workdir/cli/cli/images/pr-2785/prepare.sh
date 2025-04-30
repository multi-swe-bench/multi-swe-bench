#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout bdce08a793abe4744c02d537e37c9ba63601a849
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

