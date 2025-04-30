#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout f17d9672f50c5ec96816abb4924e0c0149f24036
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

