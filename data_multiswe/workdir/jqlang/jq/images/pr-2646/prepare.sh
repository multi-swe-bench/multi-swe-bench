#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout a29ac81de117a6bad625bc4ff75bbb395a58f7d6
bash /home/check_git_changes.sh
git submodule update --init

