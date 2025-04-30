#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout 32559e2175a5c793c47df0b214775affde5ac35e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

