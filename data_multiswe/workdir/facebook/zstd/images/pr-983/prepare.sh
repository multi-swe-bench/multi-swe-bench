#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 04c00f9388b5d57665792571fe46a7eadc973c8d
bash /home/check_git_changes.sh

