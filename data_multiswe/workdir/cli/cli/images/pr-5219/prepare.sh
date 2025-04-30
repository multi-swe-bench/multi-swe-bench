#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 1eefda0b459a980873167bf0fb0a653f48acfc78
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

