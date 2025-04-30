#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 8ebf87119cf958de07577c0c8b71e2ce63c5986e
bash /home/check_git_changes.sh


