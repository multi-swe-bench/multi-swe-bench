#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout f4214ae8dd9cdfcbeb5e2db66aee59d066d9cb0c
bash /home/check_git_changes.sh
mkdir build || true

