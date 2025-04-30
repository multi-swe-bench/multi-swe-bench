#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout f6d2f83938b54a38441500c9fb34a25fd8a1850a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

