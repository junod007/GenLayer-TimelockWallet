# GenLayer Milestone Escrow

A GenLayer-native milestone escrow smart contract that combines native GEN asset custody with GenLayer nondeterministic AI evaluation and consensus.

## Project Overview

GenLayer Milestone Escrow allows a client to lock native GEN in a smart contract for a project milestone.

The contract creates a complete milestone workflow:

1. The client deploys the escrow contract.
2. The client deposits native GEN into the contract.
3. The client submits project evidence.
4. GenLayer retrieves the submitted evidence from the web.
5. GenLayer AI evaluates the milestone requirement.
6. GenLayer consensus validates the evaluation.
7. The result is stored on-chain as `APPROVED` or `REJECTED`.
8. The escrow provides a settlement path for the locked GEN.

The purpose is to demonstrate a real GenLayer-specific workflow where external evidence and AI evaluation influence an on-chain escrow settlement.

---

## Milestone Requirement

The milestone requirement is defined when the contract is deployed.

Example:

> A GenLayer-native milestone escrow must accept native GEN deposits, store project evidence, retrieve the evidence through GenLayer nondeterministic web access, evaluate the milestone using GenLayer AI execution and consensus, and provide a settlement path that releases GEN after approval or refunds GEN after rejection.

---

## Participants

### Client

The client is automatically set to:

```text
gl.message.sender_address
