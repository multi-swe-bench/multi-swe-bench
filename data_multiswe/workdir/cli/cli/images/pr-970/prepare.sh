#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 84ecf324f8702963b5c45e2958ba448b7da4c0eb
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

