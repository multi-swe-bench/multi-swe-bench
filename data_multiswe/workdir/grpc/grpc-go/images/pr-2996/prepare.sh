#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout 45bd2846a34b039c5f1e69b7202f118687156b34
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

