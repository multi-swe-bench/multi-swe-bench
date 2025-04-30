#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout da4bbe398e14be2955ff5300d11fe54e6451ee18
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

