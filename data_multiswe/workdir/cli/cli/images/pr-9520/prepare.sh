#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 327451627cf59d4ab46eedb4f5c138b7cf341f7b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

