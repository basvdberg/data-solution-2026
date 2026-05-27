# Remote SSH development workflow

## Table of contents

<!-- markdown-toc:start -->
- [Recommended setup](#recommended-setup)
- [Option A: keep code local, connect to NAS services](#option-a-keep-code-local-connect-to-nas-services)
- [Option B: clone on NAS and open via Remote SSH](#option-b-clone-on-nas-and-open-via-remote-ssh)
- [Keeping both machines in sync](#keeping-both-machines-in-sync)
- [What not to do](#what-not-to-do)
<!-- markdown-toc:end -->

This repo is the **source of truth**. Remote SSH is just a way to edit and run it on another machine (for example your NAS).

## Recommended setup

- **Keep Git as the safety net**: commit locally and push to your remote (GitHub/GitLab/Azure DevOps).
- **Run infrastructure on the NAS** (Airflow / Kafka / Postgres).
- **Develop on your laptop**:
  - Either keep code local and connect to NAS services via VPN/SSH tunnels.
  - Or clone this repo on the NAS and open it over Remote SSH.

## Option A: keep code local, connect to NAS services

Use a VPN (preferred) or SSH tunnels so your local code can reach NAS services without exposing ports to the internet.

Nothing in this repo needs to move.

## Option B: clone on NAS and open via Remote SSH

1. Ensure the NAS has:
   - `git`
   - Python (matching your local version if possible)
2. Clone the repository on the NAS:

```bash
git clone <your-repo-url> data-solution-2026
cd data-solution-2026
```

3. From your laptop, connect to the NAS via your editor’s Remote SSH feature and open the cloned folder.

## Keeping both machines in sync

- Treat the NAS folder as **another clone**.
- Push/pull regularly:
  - On laptop: `git pull` / `git push`
  - On NAS: `git pull` (and `git push` only if you intentionally commit there)

## What not to do

- Don’t expose Airflow/Kafka/Postgres ports directly to the internet.
- Don’t store secrets in the repo. Keep them in `.env` (ignored) or your secret manager.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
  - Classification
  - Configuration
  - Connection
  - Convention
  - Data
    - Staging
      - Openmeteo
        - Daily_Temperature
  - Data Object
    - Source
      - Openmeteo
    - Staging
      - Openmeteo
  - Data Object Mapping
    - Staging
      - Openmeteo
  - Doc
    - Data Object Mapping
    - [Remote SSH development workflow](remote-ssh.md)
  - Extractor_And_Poller
    - Common
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
  - Output
  - Perspective
  - Schema
    - [Schema follow-ups](../schema/data-objects-schema.md)
  - Setting
  - Template
  - [DSA interface](../dsa-interface.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026)
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns)
<!-- markdown-project-structure:end -->
