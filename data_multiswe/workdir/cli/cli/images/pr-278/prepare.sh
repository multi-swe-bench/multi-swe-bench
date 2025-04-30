#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6a6a6cc60f99e940f5eb8a19a03eb0c8c04e3e72
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

