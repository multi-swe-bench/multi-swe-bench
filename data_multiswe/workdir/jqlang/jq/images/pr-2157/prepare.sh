#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout f88c4e5888d6d125695444d044df4bb55ad75888
bash /home/check_git_changes.sh
git submodule update --init

