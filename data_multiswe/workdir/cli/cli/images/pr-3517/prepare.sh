#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout ac0fe6bf715537a5fb9b99f80344ea098134a335
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

