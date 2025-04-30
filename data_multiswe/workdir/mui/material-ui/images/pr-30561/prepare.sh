#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 88aa00a1665d1c6bb642392d104c9188ee830799
bash /home/check_git_changes.sh

yarn install || true

