#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout ba8ac974aaa16ebcf00f17c653d131a3b6d74a30
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

