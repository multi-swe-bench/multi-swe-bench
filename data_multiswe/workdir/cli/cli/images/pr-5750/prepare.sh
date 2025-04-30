#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 04ed77ddf0e0766e8955ca31dbf9812d4b835eb0
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

