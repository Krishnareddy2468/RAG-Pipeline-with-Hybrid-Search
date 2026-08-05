# Developer Onboarding Guide

Owner: Platform Engineering  
Last updated: 2026-07-25

## Local Setup

New engineers should install Python 3.11 or newer, Docker Desktop, Git, and the company CLI. After cloning a service repository, copy `.env.example` to `.env` and fill in local development values.

## Branching Workflow

All feature work must happen on a feature branch. Branch names should follow this format:

```text
feature/<ticket-id>-short-description
```

Pull requests require at least one approval before merge. Any change touching authentication, billing, or customer data requires a second approval from the owning team.

## Service Configuration

Configuration values must be read from environment variables. Secrets must never be committed to GitHub. Use the internal secrets manager for API keys, database passwords, and webhook URLs.

## Deployment

Staging deployments happen automatically when a pull request is merged into `develop`. Production deployments happen from `main` after the release checklist is complete.

## Rollback

If a production deployment causes customer impact, the incident commander can trigger rollback from the deployment dashboard. The target recovery time is 15 minutes.
