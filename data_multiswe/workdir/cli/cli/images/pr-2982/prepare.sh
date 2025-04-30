#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 4e5aa91fac4f9157610f7ebe65c3a3828af65c3f
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

