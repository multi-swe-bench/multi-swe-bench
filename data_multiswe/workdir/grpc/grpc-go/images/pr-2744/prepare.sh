#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout b03f6fd5e3dfa7663a225c36a15d623159f6724b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

