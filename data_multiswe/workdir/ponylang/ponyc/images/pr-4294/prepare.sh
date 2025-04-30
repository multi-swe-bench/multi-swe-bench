#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout c026193ed8e70bad5ba6fdc2f0da23879ddec9ce
bash /home/check_git_changes.sh


