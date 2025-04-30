#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 494598ad55d70791b2992f3c60ac41801a76b2cf
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

