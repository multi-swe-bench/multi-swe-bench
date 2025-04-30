#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 22df673d577367dffdc8f31ecf67fce963ac777a
bash /home/check_git_changes.sh


