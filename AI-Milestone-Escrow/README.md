# AI Milestone Escrow

An AI-powered milestone escrow smart contract built on GenLayer.

## Overview

AI Milestone Escrow is a smart contract designed to manage milestone-based agreements between a client and a service provider.

The contract allows a client to define a milestone requirement and submit evidence when the milestone has been completed. The submitted evidence can then be evaluated using GenLayer's intelligent contract capabilities.

Based on the evaluation result, the milestone can be accepted or rejected.

## Features

- Create a milestone agreement
- Define a client name
- Define milestone requirements
- Submit evidence through a URL
- Store submitted evidence
- AI-powered milestone evaluation
- Automatic decision recording
- Store evaluation reasons
- Track review status
- Query milestone information
- Query evidence URL
- Query evaluation decision
- Query evaluation reason
- Check contract status

## Contract Flow

```text
Client creates milestone
        |
        v
Milestone requirement is stored
        |
        v
Evidence URL is submitted
        |
        v
Evidence is evaluated
        |
        v
AI evaluation produces a decision
        |
        +-------------------+
        |                   |
        v                   v
     ACCEPTED            REJECTED
