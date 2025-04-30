#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout aa4eae656c8137762f4cb0065e80178b77acf2dc
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

