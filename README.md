# Evidence Delivery Escrow

A smart contract built on GenLayer for managing escrow-style delivery verification using submitted evidence and AI-assisted review.

## Overview

Evidence Delivery Escrow allows a client to define a delivery requirement and an escrow amount for a provider.

The provider submits evidence of completion through an evidence URL. The contract then uses GenLayer's non-deterministic execution and comparative consensus mechanism to review whether the submitted evidence reasonably satisfies the requirement.

## Features

- Stores client and provider information
- Stores an escrow amount
- Defines a delivery requirement
- Allows the provider to submit evidence
- Uses an evidence URL as proof of delivery
- Reviews evidence using AI-assisted evaluation
- Uses GenLayer comparative consensus
- Approves or rejects submitted evidence
- Allows the client to release payment after approval
- Allows the client to request a refund

## Contract Flow

1. Deploy the contract with:
   - Provider address
   - Escrow amount
   - Delivery requirement

2. The provider submits an evidence URL using:

   `submit_evidence(url)`

3. The contract evaluates the submitted evidence using:

   `review_evidence()`

4. The evidence is reviewed against the original requirement.

5. If approved, the client can call:

   `release_payment()`

6. If the evidence is rejected or the escrow is not settled, the client can call:

   `refund_client()`

## Read Methods

- `get_status()`
- `get_evidence()`
- `get_amount()`

## Write Methods

- `submit_evidence(url)`
- `review_evidence()`
- `release_payment()`
- `refund_client()`

## Contract States

The contract can use the following states:

- `pending`
- `evidence_submitted`
- `approved`
- `rejected`
- `refunded`

## Evidence Review

The contract uses GenLayer's:

- `gl.nondet.exec_prompt`
- `gl.eq_principle.prompt_comparative`

The AI reviewer compares the submitted evidence against the original escrow requirement and returns an `approved` or `rejected` decision.

## Source Code

Main contract source:

`EvidenceDeliveryEscrow.py`

## Development

Built and deployed using GenLayer Studio.

This repository also contains other GenLayer smart contract experiments, including:

- GenLayer Timelock Wallet
- AI Milestone Escrow
