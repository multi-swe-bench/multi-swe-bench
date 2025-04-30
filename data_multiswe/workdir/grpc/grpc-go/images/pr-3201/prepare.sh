#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout 7c1d326729dc9b0a07135f8902ddcc050ff8ab64
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

