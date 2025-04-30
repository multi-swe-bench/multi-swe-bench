#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 6446dfbbfba408f9771540d24168ca6ee725c34c
bash /home/check_git_changes.sh


    