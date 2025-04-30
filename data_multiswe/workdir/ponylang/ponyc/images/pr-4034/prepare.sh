#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout bafd65652fb97068271a5c462066bcc1a433f82f
bash /home/check_git_changes.sh


