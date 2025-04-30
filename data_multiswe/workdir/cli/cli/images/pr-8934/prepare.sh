#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 4896546432354fdf2dbf6cc06ddc26efecd471d5
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

