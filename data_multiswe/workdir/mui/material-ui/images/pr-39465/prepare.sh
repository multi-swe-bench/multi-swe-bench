#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout c13dfc7dcf892358430a6bd520c7ea04049ce1ca
bash /home/check_git_changes.sh

yarn install || true

