#!/bin/bash
set -e

cd /home/tokio
git apply /home/test.patch /home/fix.patch
cargo test

