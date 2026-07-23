# Threshold Network tBTC Bridge - Vulnerability Laboratory & PoC

## Overview
This repository contains a high-fidelity cryptographic proof of concept (PoC) demonstrating a severe systemic race condition and arithmetic underflow vulnerability discovered within the Threshold Network ecosystem.

**Author:** Ramón Rivas (@jramonrivasg)
**Status:** Secured / Pre-disclosure Archive
**Target Module:** `RebateStaking.sol` & Associated Cross-Chain Transit Pipes

## Impact Architecture
The vulnerability manifests as an arithmetic `Panic(0x11)` detonation resulting from concurrent multi-transaction sequence execution within a single block boundary. By corrupting the indexing structures, it fully brick-locks operational functions on downstream deposit/redemption modules (`Deposit.sol`, `Redemption.sol`), inducing an immediate and permanent Denial of Service (DoS) condition on all capital in transit.

## Steps to Reproduce
1. Initialize a clean standalone Forge environment: `forge init .`
2. Run execution test suite: `forge test -vvvv`
