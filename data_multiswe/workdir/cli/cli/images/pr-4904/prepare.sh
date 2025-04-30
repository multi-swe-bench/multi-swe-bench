#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 4bbbf4632179a5074ab49df6489a55d08f163d6f
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

