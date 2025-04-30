#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout d323783a0f1e3f489d1102e6760008e297c0050d
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

