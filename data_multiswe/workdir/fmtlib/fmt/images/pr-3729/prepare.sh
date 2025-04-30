#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 5cfd28d476c6859617878f951931b8ce7d36b9df
bash /home/check_git_changes.sh
mkdir build || true

