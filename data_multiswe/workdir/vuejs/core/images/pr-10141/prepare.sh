#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 07922dacc7422e828eb4238eac58dd11cd2cdb5c
bash /home/check_git_changes.sh

pnpm install || true

