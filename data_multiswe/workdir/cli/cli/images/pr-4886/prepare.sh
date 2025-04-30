#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e4f1a676f09b5e08bbbf9a784768d689c3935b4e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

