#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout 74c41e8c5e927e6b8aa0b04744fdb6d50fb6fc70
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

