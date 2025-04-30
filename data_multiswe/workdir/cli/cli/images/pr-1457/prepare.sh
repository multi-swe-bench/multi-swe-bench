#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 88eaa28aef1f1539abbcb3ce6580cce9122e783a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

