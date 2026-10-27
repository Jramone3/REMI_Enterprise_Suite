# RESEARCH ADVISORY: CRITICAL SOUNDNESS VULNERABILITY IN ZK-CIRCUITS

## Abstract / Executive Summary
An independent security research finding reveals a critical soundness vulnerability within zero-knowledge circuits (qp-zk-circuits) operating on a Substrate-based Layer 1 blockchain architecture. The flaw arises from an unconstrained type conversion boundary between primitive u128 runtime parameters and finite field elements, allowing controlled modular reduction (mathematical wrap-around). This enables deterministic cryptographic collisions with legitimate state commitments and nullifiers in private transaction schemes.

## Technical Scope & Vulnerability Class
* Vulnerability Type: Cryptographic Soundness Bug / Uncontrolled Modular Reduction / Nullifier Collision.
* Architecture Impacted: Zero-Knowledge Circuit Gates, State Commitment Verification, and Privacy Subsystems within a production-grade Substrate L1 runtime.
* Severity Classification: Critical (Direct compromise of cryptographic uniqueness and double-spending protection).

## Attack Vector & Impact
1. State Manipulation: An attacker can forge an alternative u128 parameter exceeding the prime modulus, which implicitly reduces to an identical finite field element during circuit preprocessing or validation.
2. Double-Spending / Nullifier Replay: Because the crafted input yields a colliding field representation, the verification layer fails to distinguish between a spent nullifier and a maliciously generated alternative representation. This breaks the uniqueness constraints required for private transfers and state commitments.

## Verification & Artifacts Available
The research package includes:
* Detailed mathematical and architectural breakdown of the conversion boundary flaw.
* A self-contained, reproducible PoC script (written in Rust) demonstrating exact finite field collisions via wrapping_add logic against prime moduli.
* Proposed secure remediation logic (strict range checking prior to field mapping).

## Disclosure Terms
This finding is held under independent secure research protocols. Detailed code artifacts, exact protocol targets, and reproduction scripts will be disclosed exclusively upon agreeing to coordinated disclosure terms and compensation frameworks.
