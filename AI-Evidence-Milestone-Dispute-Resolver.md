# AI Evidence Milestone Dispute Resolver

A GenLayer smart contract that resolves milestone delivery disputes using AI-based evaluation of submitted evidence.

## Overview

This contract allows a client and provider to manage a milestone delivery dispute.

The provider submits a public evidence URL. The client can open a dispute after evidence has been submitted. The contract then retrieves the evidence from the URL and uses GenLayer's non-deterministic AI execution to evaluate whether the submitted evidence satisfies the milestone requirement.

The AI evaluation produces one of two outcomes:

- `APPROVE` → `RELEASE_TO_PROVIDER`
- `REJECT` → `REFUND_TO_CLIENT`

## Contract

**Contract name**

`AIEvidenceMilestoneDisputeResolver`

**Source code**

`ai_evidence_milestone_dispute_resolver.py`

## Contract Address

```text
0x5E15Db5503E27ab66B0b00E023c8B93f515E273E
```

## Workflow

```text
Provider submits evidence
          ↓
Client opens dispute
          ↓
Anyone calls resolve_dispute
          ↓
Contract fetches evidence URL
          ↓
AI evaluates requirement and evidence
          ↓
APPROVE or REJECT
          ↓
RELEASE_TO_PROVIDER or REFUND_TO_CLIENT
```

## Main Functions

### `submit_evidence(evidence_url)`

Can only be called by the provider.

Stores a public URL containing evidence related to the milestone.

The contract prevents duplicate evidence submissions.

### `open_dispute()`

Can only be called by the client.

The dispute can only be opened after evidence has been submitted.

### `resolve_dispute()`

Runs the AI evidence evaluation.

The contract:

1. Fetches evidence using `gl.nondet.web.get`.
2. Extracts the evidence content.
3. Sends the requirement and evidence to an AI evaluator.
4. Requests structured JSON output.
5. Validates the AI result through GenLayer validator consensus.
6. Stores the final decision, reasoning, and resolution.

## AI Evaluation

The AI evaluator receives:

- The milestone requirement.
- The submitted evidence URL.
- Evidence content fetched from the public source.

The expected evaluation result is:

```json
{
  "decision": "APPROVE",
  "reasoning": "Brief evidence-based explanation",
  "resolution": "RELEASE_TO_PROVIDER"
}
```

Possible values are:

| Decision | Resolution |
|---|---|
| `APPROVE` | `RELEASE_TO_PROVIDER` |
| `REJECT` | `REFUND_TO_CLIENT` |

## Consensus Validation

The contract uses:

```python
gl.vm.run_nondet_unsafe(
    evaluate_evidence,
    validate_result
)
```

The leader evaluates the evidence and returns a structured result.

Validators independently evaluate the same evidence and compare the leader's:

- `decision`
- `resolution`

The transaction reaches consensus when the validators accept the result according to GenLayer's consensus process.

## State Variables

| Variable | Description |
|---|---|
| `client` | Address of the contract creator |
| `provider` | Address authorized to submit evidence |
| `requirement` | Milestone requirement |
| `evidence_url` | Public URL of submitted evidence |
| `evidence_submitted` | Indicates whether evidence was submitted |
| `dispute_open` | Indicates whether a dispute is active |
| `resolved` | Indicates whether the dispute was resolved |
| `decision` | Final AI decision |
| `reasoning` | Evidence-based explanation |
| `resolution` | Final release or refund outcome |

## Public State

The contract provides:

```python
get_contract_state()
```

This returns the current state, including:

- Client
- Provider
- Requirement
- Evidence URL
- Evidence submission status
- Dispute status
- Resolution status
- AI decision
- Reasoning
- Final resolution

## Tested Execution Flow

The following flow was successfully executed on GenLayer Studio:

1. Contract deployment
2. `submit_evidence`
3. `open_dispute`
4. `resolve_dispute`
5. `get_contract_state`

The successful evaluation produced:

```text
decision: APPROVE
resolution: RELEASE_TO_PROVIDER
resolved: True
```

## Evidence

The test used a public GitHub raw URL as the evidence source:

```text
https://raw.githubusercontent.com/junod007/GenLayer-TimelockWallet/refs/heads/main/ai_evidence_milestone_dispute_resolver.py
```

## Technical Notes

The implementation handles GenLayer AI responses that may be returned as either:

- A JSON string
- A dictionary-like structured result

The evaluation result is normalized before it is processed by the contract.

This avoids errors such as:

```text
TypeError: the JSON object must be str, bytes or bytearray, not dict
```

## Project Goal

The goal of this contract is to demonstrate a decentralized AI-assisted dispute resolution workflow where milestone evidence is:

1. Submitted by a provider.
2. Publicly retrievable.
3. Evaluated against a defined requirement.
4. Reviewed through GenLayer's validator consensus process.
5. Converted into an on-chain resolution.

## License

Experimental project built for the GenLayer ecosystem.
