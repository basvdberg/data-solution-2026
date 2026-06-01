# Lessons learned

## Table of contents

<!-- markdown-toc:start -->
- [Infrastructure deployment](#infrastructure-deployment)
- [Keep in control of Gen AI / continuous refactoring](#keep-in-control-of-gen-ai-continuous-refactoring)
- [Data extraction via API](#data-extraction-via-api)
- [Learning new tools](#learning-new-tools)
- [Agnostic Data Labs](#agnostic-data-labs)
- [Data Solution Automation metadata](#data-solution-automation-metadata)
<!-- markdown-toc:end -->

## Infrastructure deployment

During this proof of concept I needed [Apache Airflow](https://airflow.apache.org/) and [Apache Kafka](https://kafka.apache.org/). To avoid cloud spend on throwaway infrastructure, I hosted both on a local QNAP NAS (“Basnas”). That required [Cursor Remote SSH](doc/design/ci-cd.md#test-on-nas-using-cursor-remote-ssh) so the agent could edit files and run commands on the NAS—installing and tuning services from prompts worked well once SSH was in place. The full workflow is in [CI/CD workflow (local + NAS)](doc/design/ci-cd.md).

I still spent noticeable time on HTTPS and local DNS so services have friendly URLs (for example `https://kafka.basnas`). To keep browser access manageable, I added a small sync tool that merges Chrome and Brave bookmarks with Basnas service URLs from deployment config.

## Keep in control of Gen AI / continuous refactoring

A pitfall when using GenAI is generating too much. Because it is easy to change the design, scope can grow quickly. A good design is also a simple one, as described in the [Simplicity](https://github.com/basvdberg/data-engineering-design-patterns/blob/main/design-patterns/generic/simplicity.md) design pattern.

I used two controls:

- **Review every change** — although I sometimes clicked “Keep all” without reading every diff.
- **Refactor deliberately** — as understanding evolved, I deleted outdated design documents and asked Cursor to rewrite them, dropping historical decisions that no longer fit.

**Takeaway:** Treat generated artefacts as drafts; pair GenAI speed with human review and occasional “reset and rewrite” when the design has drifted.

## Data extraction via API

**Before:** Extracting from a source with a well-defined API typically took one to two weeks—collecting and reading sometimes incomplete documentation, then iteratively building and testing the client.

**After:** With generative AI (Cursor in this project), the [Open-Meteo extractor](extractor_and_poller/readme.md) was produced in a handful of prompts. End-to-end validation, including a smoke test against the live service, fit within about an hour.

**Takeaway:** A large efficiency gain; in this PoC the generated client was stronger and faster to test than a typical hand-written first version.

## Learning new tools

**Before:** Learning Airflow, Kafka, [Agnostic Data Labs (ADL)](https://docs.agnosticdatalabs.com/docs/), or a new protocol client is normal work, but it often costs weeks of courses and trial-and-error before you ship confidently.

**After:** AI explains how a tool fits a concrete use case in *your* architecture and generates starter code (DAGs, parsers, mapping JSON). You learn from working examples without mastering every aspect of the tool first. That shortens time-to-market for new tooling, makes it easier to compare or replace components, and supports a more technology-agnostic architecture.

**Takeaway:** Use GenAI for guided onboarding and scaffolding; keep [metadata in Git](doc/design/meta-data-design.md) as the stable specification while you experiment with *how* to run it.

## Agnostic Data Labs

[Agnostic Data Labs](https://docs.agnosticdatalabs.com/docs/) is a free companion to visualize [DSA metadata](https://data-solution-automation-engine.github.io/data-warehouse-automation-metadata-schema/). The UI and feature set are impressive, but I hit showstoppers for this PoC:

1. JSON produced to match the published automation schema did not load correctly in ADL, with little feedback on *why* (validation errors were hard to surface). After reporting this to the developer it was fixed quickly. 
2. ADL decomposes JSON into elemental components, which changes the on-disk representation. For round-tripping and GenAI workflows, a model centred on those components might be clearer than top-level `dataObjectMappings` alone.

For this proof of concept, ADL is a nice to have because of the show stoppers. I decided to keep it out of this POC.

## Data Solution Automation metadata

[Data Solution Automation (DSA)](https://github.com/data-solution-automation-engine/data-warehouse-automation-metadata-schema) metadata is an open JSON exchange format for connections, data objects, and source-to-target mappings—the *what* of a data solution without locking it to one ETL product or cloud stack. [Roelant Vos](https://roelantvos.com/blog/interface-for-data-warehouse-automation-metadata-released/) has written about the intent behind this kind of portable automation metadata for years.

After more than twenty years in data engineering I have seen frameworks and vendors change constantly, while the underlying transformation logic stays much the same. Describing that logic in a shared, human-readable standard pays off:

1. **Shared vocabulary** — other engineers can read mappings and data objects without learning a project-specific config dialect.
2. **Longer-lived specifications** — Data solution specification can outlive the life of a data solution implementation because it can be reused in a new platform or tooling.
3. **Ecosystem and conventions** — Using common standards allows us to collaborate.

However, when working with DSA In this proof of concept, I hit the following issues:
1. The schema defines data object mappings as one condensed JSON schema, containing data objects and connections. I think it's better to describe those elemental objects separately instead of in a condensed form, so that we don't have any redundancy when, for example, a data object is used in multiple mappings. This is also done when reading this DSA schema by the ADL tool.
2. I think metadata should be as simple as possible And easy to read and understand. For this reason, I think it's good To define identities as local reference paths instead of hash codes. This way, the identity reveals the name and location of the artifact. This also makes the name attribute redundant.

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
  - [Browser bookmarks sync](https://github.com/basvdberg/browser-bookmarks-sync)
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026)
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns)
<!-- markdown-project-structure:end -->
