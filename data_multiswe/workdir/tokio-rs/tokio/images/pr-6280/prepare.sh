#!/bin/bash
set -e

cd /home/tokio
git reset --hard
bash /home/check_git_changes.sh
git checkout e4f9bcb5775a8cbbc848aedea3ad49aa60dd1dae
bash /home/check_git_changes.sh

cargo test || true

