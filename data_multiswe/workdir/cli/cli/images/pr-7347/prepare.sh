#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 350011162a66810b8515886cddea9ec1cfac49d8
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

