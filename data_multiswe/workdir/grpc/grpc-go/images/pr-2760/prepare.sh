#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout e33051174bc15b756823131f1161f46a4b265c3a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

