#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout 5878d965b2234619fe67d256d0cd582553e7fff1
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

