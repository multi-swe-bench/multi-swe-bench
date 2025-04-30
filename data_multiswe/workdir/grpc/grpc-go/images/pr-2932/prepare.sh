#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout 61f27c14152c7551d5cc657c31e81a3597c82e48
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

