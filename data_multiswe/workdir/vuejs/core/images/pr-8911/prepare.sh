#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 3be4e3cbe34b394096210897c1be8deeb6d748d8
bash /home/check_git_changes.sh

pnpm install || true

