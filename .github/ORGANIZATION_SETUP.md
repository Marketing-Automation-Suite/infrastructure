# GitHub Organization Setup Guide

This document outlines the organization-level setup for Marketing-Automation-Suite.

## Repository Settings

### Branch Protection Rules

All repositories should have:
- Require pull request reviews before merging
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Include administrators
- Restrict pushes that create matching branches

### Default Branch

All repositories use `main` as the default branch.

## GitHub Projects

### Main Project: Marketing Automation Suite

Track all repositories in a single project with:
- Status columns: Backlog, In Progress, Review, Done
- Automation rules
- Repository linking

## Repository Structure

1. **infrastructure** - Main orchestration repo
2. **xlam-server** - AI function calling service
3. **n8n-orchestration** - Workflow orchestration
4. **crm-twenty** - CRM service
5. **mautic-integration** - Marketing automation
6. **analytics-lightdash** - Business intelligence
7. **dashboard-streamlit** - Dashboard UI
8. **shared-libraries** - Shared code

## CI/CD Setup

Each repository has GitHub Actions workflows for:
- Testing
- Building Docker images
- Deployment (when applicable)

## Security

- Dependabot enabled for all repositories
- Secret scanning enabled
- Code scanning (if applicable)

