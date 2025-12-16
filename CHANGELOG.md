# Changelog

All notable changes to the infrastructure repository will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial infrastructure repository setup
- Docker Compose configuration with Postgres and Redis
- Service placeholders for all 10 repositories
- Git submodule setup scripts
- Basic documentation structure
- Health checks for infrastructure services

### Infrastructure Services
- PostgreSQL 15 (Alpine)
- Redis 7 (Alpine)
- Docker networking configuration
- Volume management for data persistence

### Scripts
- `setup-dev.sh` - Clone all service repositories
- `update-all.sh` - Update all git submodules

