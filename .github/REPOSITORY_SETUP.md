# Repository Setup Checklist

This checklist should be applied to each repository in the organization.

## ✅ Repository Settings

- [x] Default branch set to `main`
- [x] Issues enabled
- [x] Projects enabled
- [x] Wiki enabled (if needed)
- [x] Branch protection rules configured
- [x] Dependabot enabled
- [x] Security alerts enabled

## ✅ Branch Protection

For each repository, configure:
- Require pull request reviews (1 approval minimum)
- Require status checks to pass
- Require branches to be up to date
- Include administrators
- Allow force pushes: No
- Allow deletions: No

## ✅ GitHub Actions

Each repository should have:
- CI workflow for testing
- Build workflow for Docker images
- Deployment workflow (if applicable)

## ✅ Documentation

Each repository should include:
- README.md with setup instructions
- API documentation (if applicable)
- Contributing guidelines (link to main CONTRIBUTING.md)
- Code of Conduct (link to main CODE_OF_CONDUCT.md)

## ✅ Labels

Standard labels for all repositories:
- `bug`
- `enhancement`
- `documentation`
- `question`
- `help wanted`
- `good first issue`
- `priority: high`
- `priority: medium`
- `priority: low`

## ✅ Webhooks (if needed)

Configure webhooks for:
- CI/CD integration
- Monitoring
- Notifications

