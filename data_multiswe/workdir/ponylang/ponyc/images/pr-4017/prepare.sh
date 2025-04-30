#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 10f8a8bc0810b80e0f7ab3aa09fafba98e9f2227
bash /home/check_git_changes.sh


