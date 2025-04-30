#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e876b229634b02d40bdfbb15844d4d3e9f121c27
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

