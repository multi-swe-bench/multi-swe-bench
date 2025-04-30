#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout adc7aa794cea8e9a80502bb247ae6aa78739d440
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

