#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e930122a0c3413b3f9bd37686dbde5beafc74b07
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

