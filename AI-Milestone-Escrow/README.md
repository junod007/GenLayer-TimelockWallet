# AI Milestone Escrow

An AI-powered milestone evidence review smart contract built on GenLayer.

## Project Overview

AI Milestone Escrow is a smart contract that allows a client to define a project milestone requirement and submit evidence of completed work.

The contract uses GenLayer's nondeterministic AI execution to independently evaluate the submitted evidence.

## Milestone Requirement

The milestone requirement is defined by the client when the contract is deployed.

Example:

The submitted project must provide a working smart contract that reviews project evidence using AI and returns either APPROVED or REJECTED.

## Evidence Submission

The contract accepts two pieces of evidence:

1. A README or project documentation URL.
2. A public source code URL.

These URLs are submitted using the `submit_evidence` method.

## AI Evidence Review

The `review_evidence` method performs the following process:

1. Checks that both README and source code evidence have been submitted.
2. Fetches the README content from the submitted URL.
3. Fetches the source code from the submitted URL.
4. Provides the milestone requirement, documentation, and source code to an AI reviewer.
5. Requires the AI reviewer to return a JSON result containing:
   - `decision`
   - `reason`
6. Validates that the decision is exactly either `APPROVED` or `REJECTED`.
7. Stores the final decision and evaluation reason on-chain.

## Contract Workflow

### 1. Deploy the Contract

Deploy the `MilestoneReviewer` contract with:

- Client name
- Milestone requirement

### 2. Submit Evidence

Call:

```text
submit_evidence(readme_url, source_code_url)
