#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout b88d2d74656f2b9833cc78c088ebf899d2189230
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

