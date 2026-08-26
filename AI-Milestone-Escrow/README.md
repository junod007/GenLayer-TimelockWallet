# GenLayer AI Milestone Escrow V3

A native GEN milestone escrow smart contract powered by GenLayer.

This contract combines:
- Native GEN escrow custody
- Milestone-based payments
- Evidence submission
- AI-assisted milestone evaluation
- GenLayer nondeterministic web access
- Validator-based consensus
- Automatic settlement based on the final decision

---

## Overview

GenLayerMilestoneEscrowV3 is an escrow contract designed for milestone-based work.

A client deposits native GEN into the escrow contract.

The provider submits work and evidence through publicly accessible project documentation and source code.

GenLayer validators independently evaluate the submitted evidence using AI and reach consensus on whether the milestone has been satisfied.

The final decision is:

- `APPROVED` → funds are released to the provider
- `REJECTED` → funds are refunded to the client

The contract stores the complete evaluation result and settlement state on-chain.

---

## Workflow

```text
Client
  |
  | Deploy Contract
  v
GenLayerMilestoneEscrowV3
  |
  | Deposit native GEN
  v
Funds Locked
  |
  | Submit Evidence
  v
Evidence Available
  |
  | Evaluate Milestone
  v
GenLayer AI Review
  |
  |-- Web Evidence Retrieval
  |-- README Review
  |-- Source Code Review
  |-- Independent Validator Review
  |
  v
GenLayer Consensus
  |
  +----------------------+
  |                      |
APPROVED              REJECTED
  |                      |
  v                      v
Provider              Client
receives GEN         receives refund
