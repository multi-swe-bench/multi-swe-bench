#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 63094461621f8e91217d9b89f513f53e21670bd9
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

