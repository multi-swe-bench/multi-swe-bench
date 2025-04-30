#!/bin/bash
set -e

cd /home/nushell
git apply /home/test.patch /home/fix.patch
cargo test

