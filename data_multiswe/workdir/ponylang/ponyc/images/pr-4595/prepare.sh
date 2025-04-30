#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout f8a2feebba3aea298bde89d445ad35ca48602ca7
bash /home/check_git_changes.sh


