#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout af05219b70c5e18542ebb499b18a1dff6ffacc6d
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

