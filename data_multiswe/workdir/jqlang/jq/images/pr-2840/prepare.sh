#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout 4cf1408e0bbac8fc714b051fe420921905128efd
bash /home/check_git_changes.sh
git submodule update --init

