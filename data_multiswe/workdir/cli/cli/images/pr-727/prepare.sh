#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e066e98a9af5345cd3a88507bae55a7eb00d1259
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

