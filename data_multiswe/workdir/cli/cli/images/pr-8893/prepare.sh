#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout ec812a16f77df5f196189e9871722b9b601143bc
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

