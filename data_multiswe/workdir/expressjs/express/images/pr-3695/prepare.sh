#!/bin/bash
set -e

cd /home/express
git reset --hard
bash /home/check_git_changes.sh
git checkout 3ed5090ca91f6a387e66370d57ead94d886275e1
bash /home/check_git_changes.sh

npm install || true

