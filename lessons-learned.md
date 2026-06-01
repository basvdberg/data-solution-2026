# Lessons learned

## Table of contents

<!-- markdown-toc:start -->
- [Data extraction via API](#data-extraction-via-api)
- [Learning new tools](#learning-new-tools)
- [Agnostic Data Labs](#agnostic-data-labs)
<!-- markdown-toc:end -->

## Data extraction via API

**Before:** Extracting from a source with a well-defined API typically took one to two weeks - collecting and reading sometimes incomplete documentation, then iteratively building and testing the client.

**After:** With generative AI (Cursor in this project), the Open-Meteo extractor was produced in a handful of prompts. End-to-end validation, including a smoke test against the live service, fit within about an hour.

**Takeaway:** A large efficiency gain, and in this PoC the generated client code was stronger and faster to test than a typical hand-written first version.

## Learning new tools

**Before:** Learning Airflow, Kafka, ADL, or a new protocol client is normal work, but it often costs weeks of courses and trial-and-error before you ship confidently.

**After:** AI explains how a tool fits a concrete use case in *your* architecture and generates starter code (DAGs, parsers, mapping JSON). You learn from working examples without mastering every aspect of the tool first. That shortens time-to-market for new tooling, makes it easier to compare or replace components, and supports a more technology-agnostic architecture.

## Agnostic Data Labs

Although the look, feel, and offered functionalities of this tool are impressive, I hit some showstoppers:

1. A JSON file generated according to the published automation schema was not read correctly by the tool, with no easy way to find out what was going on.
2. The tool converts the JSON into elemental components. This alters the underlying JSON representation. It may make sense to represent elemental components in the first place instead of `DataObjectMappings`.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](readme.md)
  - Connection
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
    - Data Solution
      - Data Object Mapping
    - Design
      - [Architecture](doc/design/architecture.md)
      - [CI/CD workflow (local + NAS)](doc/design/ci-cd.md)
      - [Event-based orchestration plan (single data object)](doc/design/event-based-orchestration-plan.md)
      - [Meta data design](doc/design/meta-data-design.md)
  - Extractor_And_Poller
    - Common
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
  - Setting
  - Template
  - [Getting started](getting-started.md)
  - [Lessons learned](lessons-learned.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026)
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns)
<!-- markdown-project-structure:end -->
