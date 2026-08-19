# AI Milestone Escrow

A milestone review smart contract built on GenLayer.

## Overview

AI Milestone Escrow is a smart contract designed to manage
milestone-based agreements and supporting evidence.

The contract allows a client to define a milestone requirement
when deploying the contract.

Evidence can later be submitted by providing:

- A README or project documentation URL
- A source code URL

The contract stores the submitted evidence on-chain and maintains
the current milestone status.

## Features

- Define a client name
- Define a milestone requirement
- Submit README evidence URL
- Submit source code evidence URL
- Store milestone status
- Approve the milestone

## Smart Contract

The contract includes the following public methods:

### Read Methods

- `get_client_name()`
- `get_milestone()`
- `get_readme_url()`
- `get_source_code_url()`
- `get_status()`

### Write Methods

- `submit_evidence(readme_url, source_code_url)`
- `approve()`

## Workflow

1. Deploy the contract with a client name and milestone requirement.
2. Submit documentation and source code evidence.
3. Review the submitted evidence.
4. Approve the milestone.
5. Check the current status.

## Built With

- Python
- GenLayer
- GenLayer Studio

## Project Structure

```text
AI-Milestone-Escrow/
├── AI_Milestone_Escrow.py
└── README.md
