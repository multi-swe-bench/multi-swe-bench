#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout c35d725b0b89ef090aab17171d091f4630eed5ca
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

