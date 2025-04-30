#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout f4be7ab10be074bf02ababb23ce15ed386c98b78
bash /home/check_git_changes.sh

yarn install || true

