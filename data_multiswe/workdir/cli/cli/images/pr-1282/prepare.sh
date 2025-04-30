#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 4b87f5b18a22207fd0d66b7fb1d68576d5f4697d
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

