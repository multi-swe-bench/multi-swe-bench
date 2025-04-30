#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 70c3ca32365f0cd6b119a24be788e4559b88b6b3
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

