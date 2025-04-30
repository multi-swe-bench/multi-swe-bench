#!/bin/bash
set -e

cd /home/bytes
git reset --hard
bash /home/check_git_changes.sh
git checkout f514bd38dac85695e9053d990b251643e9e4ef92
bash /home/check_git_changes.sh

cargo test || true

