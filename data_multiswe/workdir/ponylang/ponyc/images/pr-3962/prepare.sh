#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 12466227bb253b600b7a3ee995b56b442d02b6e2
bash /home/check_git_changes.sh


