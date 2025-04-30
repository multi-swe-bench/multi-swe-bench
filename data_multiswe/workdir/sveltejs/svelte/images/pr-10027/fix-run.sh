#!/bin/bash
set -e

cd /home/svelte
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
pnpm test -- --reporter verbose 

