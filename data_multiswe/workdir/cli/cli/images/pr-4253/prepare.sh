#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e6ff77ce73c201b0ee36d2b802ea45e9e1ad1822
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

