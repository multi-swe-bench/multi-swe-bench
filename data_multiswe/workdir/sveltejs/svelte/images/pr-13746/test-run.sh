#!/bin/bash
set -e

cd /home/svelte
git apply --whitespace=nowarn /home/test.patch
pnpm test -- --reporter verbose 

