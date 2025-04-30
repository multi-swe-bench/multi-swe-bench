#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout df7614f0e919e939ad93fc78595b5ebc3bae474f
bash /home/check_git_changes.sh


