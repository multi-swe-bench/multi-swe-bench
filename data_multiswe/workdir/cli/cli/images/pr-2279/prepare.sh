#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e093d235215f8c06a45204123a725c25aef692b6
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

