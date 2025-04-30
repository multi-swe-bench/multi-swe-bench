#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b8a1ff6e70dc9bbe12a8ffdb5644889de6be48a4
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

