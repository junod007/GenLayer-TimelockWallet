# Evidence Delivery Escrow V2

A GenLayer Intelligent Contract for escrow-based delivery verification using
contract-side web evidence retrieval, LLM-assisted evaluation, comparative
consensus, and actual on-chain payment settlement.

## Overview

Evidence Delivery Escrow V2 is designed for delivery workflows where a client
deposits funds for a provider and the provider submits a publicly accessible
URL as evidence of delivery.

The contract combines:

- Payable escrow custody
- Contract-side web retrieval
- LLM-based evidence evaluation
- GenLayer comparative consensus
- Actual payment settlement
- Refund handling after rejected evidence

The goal is to make the evidence review process verifiable and connected to
actual escrow funds rather than only storing a review result.

---

## Contract

**Contract name:**

`EvidenceDeliveryEscrowV2`

**Source file:**

`evidence_delivery_escrow_v2.py`

**Directory:**

`Evidence-Delivery-Escrow-V2/`

---

## Core Flow

The contract follows this lifecycle:

```text
Client
  │
  │ Deploy contract
  ▼
EvidenceDeliveryEscrowV2
  │
  │ deposit()
  │
  ▼
Escrow holds funds
  │
  │ Provider submits evidence URL
  ▼
submit_evidence()
  │
  │ Contract retrieves URL content
  ▼
Web evidence content
  │
  │ LLM evaluation
  ▼
Comparative consensus
  │
  ├── approved ──► Client releases payment ──► Provider
  │
  └── rejected ──► Client requests refund ──► Client
