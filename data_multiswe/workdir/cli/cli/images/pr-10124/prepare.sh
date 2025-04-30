#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 64c23e5e9540fe8ac722aefaa967852600215f4f
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

