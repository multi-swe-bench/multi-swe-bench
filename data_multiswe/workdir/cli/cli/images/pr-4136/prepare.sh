#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout fbe1487dd06506cbde02558ba27ff09461ff1cc4
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

