#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout f31c180e8f38c085c4366a91f9bfffc2dd7c2bc2
bash /home/check_git_changes.sh
git submodule update --init

