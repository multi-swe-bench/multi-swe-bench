#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout becb3163088e47c60652a4fcc0d982be4fd1a40e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

