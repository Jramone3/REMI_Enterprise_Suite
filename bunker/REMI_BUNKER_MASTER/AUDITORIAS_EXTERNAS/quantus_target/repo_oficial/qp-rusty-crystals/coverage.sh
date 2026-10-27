#!/bin/bash

echo "Running all unit tests and coverage with tarpaulin..."

# Check if cargo-tarpaulin is installed
if ! command -v cargo-tarpaulin &> /dev/null; then
    echo "Error: cargo-tarpaulin is not installed."
    echo "Please install it by running the following command:"
    echo ""
    echo "    cargo install cargo-tarpaulin"
    echo ""
    echo "After installation, re-run this script."
    exit 1
fi

# Run tarpaulin with all targets
cargo tarpaulin --workspace --all-targets
