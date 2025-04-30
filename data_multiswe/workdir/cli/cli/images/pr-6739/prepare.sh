#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6d93849476aa8348b36d43a3ee1b9101deaa47ec
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

