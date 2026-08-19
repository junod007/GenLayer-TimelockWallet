# AI Milestone Escrow

An AI-powered milestone review smart contract built on GenLayer.

## Overview

AI Milestone Escrow allows a client to define a project milestone requirement and submit evidence of completed work.

The submitted evidence consists of:

- A README/documentation URL
- A source code URL

The contract fetches both pieces of evidence from the web and uses GenLayer's AI capabilities to evaluate whether the submitted project satisfies the defined milestone requirement.

## Workflow

1. Deploy the `MilestoneReviewer` contract with:

   - Client name
   - Milestone requirement

2. Submit project evidence using:

   - `submit_evidence(readme_url, source_code_url)`

3. The contract stores the evidence and changes the status to:

```text
SUBMITTED
