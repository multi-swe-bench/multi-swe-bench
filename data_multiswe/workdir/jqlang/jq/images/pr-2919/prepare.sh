#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout 7f547827e47b5ade563a293329deb4226496d72f
bash /home/check_git_changes.sh
git submodule update --init

