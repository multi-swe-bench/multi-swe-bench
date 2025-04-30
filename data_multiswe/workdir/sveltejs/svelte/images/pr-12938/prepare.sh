#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 363a5418e6330356ebc7abe39d240afccd255147
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

