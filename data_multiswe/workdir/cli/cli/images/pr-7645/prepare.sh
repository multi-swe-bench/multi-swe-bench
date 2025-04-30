#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout d21c11d774df552b9c36d3d35aa8eb12e5aebd55
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

