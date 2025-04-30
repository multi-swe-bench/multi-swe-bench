#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 31dad18fb9901880a3a3c1de1db0698f32faf2d6
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

