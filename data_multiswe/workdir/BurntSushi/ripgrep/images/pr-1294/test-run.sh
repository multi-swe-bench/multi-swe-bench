#!/bin/bash
set -e

cd /home/ripgrep
git apply /home/test.patch
cargo test

