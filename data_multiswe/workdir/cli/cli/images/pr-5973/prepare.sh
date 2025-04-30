#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 954689ea9f26e3131ca816285eee8930cd8aa835
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

