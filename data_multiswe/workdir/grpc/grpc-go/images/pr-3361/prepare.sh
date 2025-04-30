#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout 648cf9b00e25b3af7839d6678a8fe319505c3b80
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

