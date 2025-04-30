#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 31a9d083bd0feaf237e7cf33b6171a1e902b7d3a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

