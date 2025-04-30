#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout ec3e02624c0b6ea726b34de08d9192d4edaacb6b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

