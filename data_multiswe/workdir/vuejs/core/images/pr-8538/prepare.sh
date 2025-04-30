#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 0e63cbfaf57979e2c6fcfa986281c7521d82d893
bash /home/check_git_changes.sh

pnpm install || true

