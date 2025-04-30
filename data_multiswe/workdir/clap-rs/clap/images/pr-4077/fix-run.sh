#!/bin/bash
set -e

cd /home/clap
git apply /home/test.patch /home/fix.patch
cargo test

