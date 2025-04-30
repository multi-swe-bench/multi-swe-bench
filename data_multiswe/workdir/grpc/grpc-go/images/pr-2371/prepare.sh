#!/bin/bash
set -e

cd /home/grpc-go
git reset --hard
bash /home/check_git_changes.sh
git checkout c1fc9faff6114b92549bd2145ac77cabff68740d
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

