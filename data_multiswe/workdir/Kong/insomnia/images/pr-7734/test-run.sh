#!/bin/bash
set -e

cd /home/insomnia
git apply --whitespace=nowarn /home/test.patch
npm test -- --verbose

