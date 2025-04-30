#!/bin/bash
set -e

cd /home/nushell
git apply /home/test.patch
cargo test

