#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout c8cf54c10c427a429663244a2ab14c4fe2dfa10a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

