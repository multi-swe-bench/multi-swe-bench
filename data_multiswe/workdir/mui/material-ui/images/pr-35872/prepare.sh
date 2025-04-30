#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout d53dff1a73f8e2b87ce3eb188fcfc4b079d898f2
bash /home/check_git_changes.sh

yarn install || true

