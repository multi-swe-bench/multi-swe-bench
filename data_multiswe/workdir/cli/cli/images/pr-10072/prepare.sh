#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 5e9283c70ced3b17f755374e908f967dabd9ecb1
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

