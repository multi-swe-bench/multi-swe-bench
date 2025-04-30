#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout ff5f0e93f53629c7f9b27f8bfe99e60fcfbeefcb
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

