#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout f7b39d80aa97614c0b4420d120b59dd192d1d521
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

