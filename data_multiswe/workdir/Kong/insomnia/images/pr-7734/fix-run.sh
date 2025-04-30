#!/bin/bash
set -e

cd /home/insomnia
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
npm test -- --verbose

