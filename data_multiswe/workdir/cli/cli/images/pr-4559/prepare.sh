#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a02d42368757288c12646537724e574afda20515
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

