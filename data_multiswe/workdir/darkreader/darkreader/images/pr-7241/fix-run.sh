#!/bin/bash
set -e

cd /home/darkreader
git apply /home/test.patch /home/fix.patch
npm run test:ci -- --json --outputFile=test-results-unit.json

