# GenLayer Milestone Escrow

A GenLayer-native milestone escrow smart contract that combines
native GEN asset custody with GenLayer nondeterministic consensus
for milestone evaluation.

## Project Overview

GenLayer Milestone Escrow allows a client to lock native GEN in an
escrow contract for a project milestone.

The provider submits public project evidence consisting of:

1. A README or project documentation URL.
2. A public source code URL.

GenLayer validators independently evaluate the submitted evidence
using nondeterministic web access and AI execution.

The resulting decision is stored on-chain as either:

- APPROVED
- REJECTED

The contract then provides a settlement path for the locked GEN.

## Why This Is GenLayer-Native

The contract uses GenLayer-specific functionality for milestone
adjudication:

- `gl.nondet.web.get()` retrieves external project evidence.
- `gl.nondet.exec_prompt()` evaluates the evidence using an AI prompt.
- `gl.vm.run_nondet_unsafe()` executes the nondeterministic evaluation
  through the GenLayer consensus workflow.

The decision is therefore not based only on a local boolean or
documentation claim. The submitted README and source code are fetched
as external evidence and evaluated through GenLayer's nondeterministic
execution.

## Escrow Asset Custody

The contract accepts native GEN through the payable `deposit()` method.

The deposited value is stored as the contract's locked escrow amount.

The escrow tracks:

- client address
- provider address
- locked amount
- milestone requirement
- evidence submission state
- review state
- approval or rejection decision
- settlement state

This creates an actual asset-backed milestone workflow rather than
a documentation-only review contract.

## Evidence Submission

The provider submits evidence using:

`submit_evidence(readme_url, source_code_url)`

The contract stores both URLs on-chain.

The evidence must be publicly accessible so GenLayer execution can
retrieve the submitted README and source code.

## Milestone Evaluation

The `evaluate_milestone()` method performs the GenLayer review.

The process is:

1. Verify that README evidence exists.
2. Verify that source code evidence exists.
3. Fetch the README using `gl.nondet.web.get()`.
4. Fetch the source code using `gl.nondet.web.get()`.
5. Provide the milestone requirement and evidence to the AI reviewer.
6. Require an `APPROVED` or `REJECTED` decision.
7. Store the decision and evaluation reason on-chain.

## Settlement

After evaluation, the contract provides a settlement path.

### APPROVED

If the milestone is approved:

`settle()` releases the locked GEN to the provider.

The contract records the escrow as released.

Status:

`RELEASED`

### REJECTED

If the milestone is rejected:

`settle()` refunds the locked GEN to the client.

The contract records the escrow as refunded.

Status:

`REFUNDED`

## Contract State

The contract exposes read methods for:

- client
- provider
- locked amount
- contract balance
- milestone requirement
- README URL
- source code URL
- decision
- evaluation reason
- status

The status flow includes:

`AWAITING_EVIDENCE`

`AWAITING_REVIEW`

`APPROVED_AWAITING_SETTLEMENT`

`REJECTED_AWAITING_REFUND`

`RELEASED`

`REFUNDED`

## Example Workflow

```text
Client
  |
  | deposit native GEN
  v
GenLayer Milestone Escrow
  |
  | provider submits README + source evidence
  v
GenLayer nondeterministic evaluation
  |
  +---- APPROVED ----> release GEN to provider
  |
  +---- REJECTED ----> refund GEN to client
