#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout d2443469605d57b6df54ce79e33d2ecc8ba9c84f
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

