# Quantus PoC: Modular Reduction Collision in qp-zk-circuits

## Overview
This proof of concept demonstrates how an uncontrolled conversion from `u128` types to finite field elements (`Fp`) without explicit range validation (`value < MODULUS`) leads to mathematical wrap-around (modular reduction). This allows crafted inputs to collide with legitimate nullifiers or commitments.

## Execution Steps
1. Ensure Rust (cargo) is installed.
2. Run the test inside this directory:
   ```bash
   cargo run --release
Verify that the assertion passes and the collision is confirmed in the console.
