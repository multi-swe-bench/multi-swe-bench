#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 0275dd329d241bdd84ce3ca0c7fc07211cb21751
bash /home/check_git_changes.sh

pnpm install || true

