#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout d79eb494d998132f060808e15521cd6a29f1b5fa
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

