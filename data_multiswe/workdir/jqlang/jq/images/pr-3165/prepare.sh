#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout 37f4cd2648faa2a4c78c3d4caf5d61cb491c7d22
bash /home/check_git_changes.sh
git submodule update --init

