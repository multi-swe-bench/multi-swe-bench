#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout 914c52b240b05e4562b1d09e5e7cf3c57495d442
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

