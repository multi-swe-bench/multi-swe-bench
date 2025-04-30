#!/bin/bash
set -e

cd /home/rayon
git apply /home/test.patch /home/fix.patch
cargo test

