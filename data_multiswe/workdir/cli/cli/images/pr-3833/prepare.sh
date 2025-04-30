#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6f34e4a6057260402c98ab9276912bd02930635c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

