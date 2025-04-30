#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout 192c8a2a3506bb69336f5c135733a3435a04fb30
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

