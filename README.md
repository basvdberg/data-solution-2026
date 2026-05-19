# Data Solution 2026

## Purpose
This project is a proof of concept to show an implementation of a data solution using the following innovations:

- Improve data engineering efficiency by AI-based code generation, in my case using [Cursor 3.3](https://cursor.com/changelog).
- Implement the ideas of the book *Data Engine Thinking* by Roelant Vos and Dirk Lerner ([dataenginethinking.com](https://dataenginethinking.com/)).
- Use the open-source [Data Solution Automation (DSA) metadata schema](https://github.com/data-solution-automation-engine/data-warehouse-automation-metadata-schema) as the standard format for source-to-target mappings, data objects, and connections.
- Use [Agnostic Data Labs (ADL)](https://docs.agnosticdatalabs.com/docs/) to visualize DSA schemas and to generate code from Handlebars templates.
- Implement the data engineering design patterns described in the companion repo [data-engineering-design-patterns](../data-engineering-design-patterns/).

## Summary

This proof of concept validated the [Purpose](#purpose) innovations in practice. The overview table maps each theme to what changed; the subsections expand the before/after comparison.

| Theme | Traditional approach | With GenAI (this PoC) |
| --- | --- | --- |
| [API extraction](#api-extraction) | One to two weeks: read incomplete docs, iterate on client code and tests | A handful of prompts; including tests, often under one hour for a well-defined API |
| [Documentation](#documentation) | Strong initial architecture doc; detail drifts and is finished late (or never) | Document each change first; review before code; docs and release notes on every PR |
| [New tools](#learning-new-tools) | Weeks of training and experimentation before productive use | Learn by example: AI explains integration and generates use-case-specific code |
| [Design patterns](#design-patterns) | Patterns implicit in tooling choices; hard to swap stacks | Patterns specify *what*; AI helps pick *how*; longer-lived, technology-agnostic design |
| [Best practices](#consolidating-best-practices) | Scattered across wikis, blogs, and individual experience | Shared, versioned pattern library the team and AI both reference |

### API extraction

**Before:** Extracting from a source with a well-defined API typically took one to two weeks—collecting and reading sometimes incomplete documentation, then iteratively building and testing the client.

**After:** With generative AI (Cursor in this project), extraction code for OData and WFS was produced in a handful of prompts. End-to-end validation, including a smoke test against the live service, fit within about an hour.

### Documentation

**Before:** Architects usually document the starting architecture well, but detailed design decisions and implementation choices are deferred until later. Under delivery pressure, documentation stays incomplete or out of date.

**After:** A better workflow is to start every change by updating documentation and only then implement. AI drafts that material quickly, so you can review the intent before code lands. Documentation and release notes can stay current on each pull request, failed approaches can be recorded for the next session, and prior docs become context for future AI calls—documentation becomes part of small CI/CD iterations instead of a separate phase.

### Learning new tools

**Before:** Learning Airflow, Kafka, ADL, or a new protocol client is normal work, but it often costs weeks of courses and trial-and-error before you ship confidently.

**After:** AI explains how a tool fits a concrete use case in *your* architecture and generates starter code (DAGs, parsers, mapping JSON). You learn from working examples without mastering every aspect of the tool first. That shortens time-to-market for new tooling, makes it easier to compare or replace components, and supports a more technology-agnostic architecture.

### Design patterns

**Before:** “How we build data pipelines” is often encoded in whichever stack the team already runs; changing tools means re‑discovering the same ideas under new names.

**After:** Generative AI pairs naturally with explicit design patterns (such as [event-based orchestration](../data-engineering-design-patterns/design-patterns/event-based-orchestration.md)): patterns state *what* must happen and abstract away vendor details. Benefits of this approach:

- **Longer solution lifetime** — patterns outlive implementations.
- **Better tool selection** — requirements and patterns can guide AI (and humans) toward fitting technology.
- **Portable best practices** — industry norms can be expressed once and reused regardless of Kafka, Airflow, or the next orchestrator.

### Consolidating best practices

**Before:** Best practices live in personal notes, scattered wiki pages, and oral tradition; new joiners and AI assistants lack one authoritative, diffable source.

**After:** This repo plus the companion [data-engineering-design-patterns](../data-engineering-design-patterns/) collection give a shared, version-controlled baseline. Metadata (DSA), generated artefacts (ADL), and pattern docs align so humans and AI apply the same rules on every change.

## Scope of this proof of concept

A single staging-layer slice from one source to the **100 Landing Area**:

- **Source:** [KNMI](https://www.knmi.nl/) daily climate observations via WFS 2.0 (free, no auth).
- **Metadata:** DSA JSON files under `DataObjectMappings/` and `DataObjects/` describe the source, the staging tables, and the mapping.
- **Generation:** ADL renders Handlebars templates in `Templates/` into staging DDL and load procedures under `Output/`.
- **Orchestration:** three generic Airflow DAGs—change detector, event controller, WFS extractor—coordinated through two Kafka topics (`events`, `commands`); PostgreSQL stores only checkpoints and an event log.
- **Patterns:** the orchestration follows [event-based orchestration](../data-engineering-design-patterns/design-patterns/event-based-orchestration.md) from the companion design patterns repo.

Out of scope for this PoC: persistent staging (`150_Persistent_Staging_Area/`), additional sources, and downstream warehouse layers. The metadata is shaped so they can be added without changing the orchestration code.

## Architecture

![High-level architecture for the staging-layer PoC](docs/architecture-staging-poc.png)

The flow, left to right:

1. **Git holds the configuration.** `DataObjectMappings/000_Source/KNMI/` describes the WFS source; `DataObjects/100_Landing_Area/` and `DataObjectMappings/Staging/` describe the staging tables and the load. Design patterns set the shape of the orchestration.
2. **Airflow + Kafka run the ingestion.** The change-detector DAG polls the WFS service on schedule and emits a `source_change` event when the dataset has new data. The event controller turns matching events into `extract` commands. The WFS extractor consumes commands, calls the source, and writes Parquet to `Data/000_Source/`. PostgreSQL stores checkpoints and the event log only—no configuration.
3. **ADL generates staging artefacts.** Reading the same DSA metadata, ADL renders the Handlebars templates in `Templates/` into DDL and load SQL under `Output/`, which load the Parquet landing files into the **100 Landing Area**.

This solution follows the [separate what and how](../data-engineering-design-patterns/design-patterns/separate-what-and-how.md) design pattern: the DSA metadata files specify *what* must happen for each source and target, while the Airflow DAGs, the WFS extractor, and the ADL-generated load procedures are implementation that specify *how* it is executed.

See [plan3.md](plan3.md) for the detailed DAG responsibilities, Kafka envelope shape, and rollout steps.

## Project layout

```text
data-solution-2026/
├── Classifications/                       Tag-based labels on data objects
├── Configurations/                        ADL project configuration
├── Connections/Sources/                   Source connection definitions
├── Conventions/                           Naming conventions
├── Data/000_Source/                       Extracted Parquet (gitignored)
├── DataObjects/
│   ├── 000_Source/                        KNMI source table definitions
│   └── 100_Landing_Area/                  Staging table definitions
├── DataObjectMappings/
│   ├── 000_Source/KNMI/                   WFS extractor config
│   └── Staging/                           Source → Landing Area mappings
├── Extractors/wfs/                        OGC WFS 2.0 client + GML parser
├── Output/                                Generated DDL, load SQL, docs
├── Schemas/                               JSON Schemas for DSA metadata
├── Settings/                              ADL settings
├── Templates/                             Handlebars templates for ADL
└── docs/                                  Architecture diagram
```

## Getting started

### Prerequisites

- Python 3.10+
- [ADL](https://docs.agnosticdatalabs.com/docs/) for metadata management and code generation
- Airflow, Kafka, and PostgreSQL when running the full orchestrated path (see [plan3.md](plan3.md))

### Run the WFS extractor (smoke test)

```powershell
pip install -r Extractors/requirements.txt

python -m Extractors.wfs --mapping knmi-daggegevens-temperature --page-size 2 --max-features 2 --limit 100
```

Output lands under `Data/000_Source/...` as defined by the `landing_path_template`
extension in `DataObjectMappings/000_Source/KNMI/knmi-daggegevens.json`.

## Available data source

| Source | Protocol | Config | Description |
| --- | --- | --- | --- |
| KNMI daggegevens | WFS 2.0 | `DataObjectMappings/000_Source/KNMI/knmi-daggegevens.json` | Daily climate observations from 33 Dutch weather stations |

## Reference

- [Data Solution Automation Schema](https://github.com/data-solution-automation-engine/data-warehouse-automation-metadata-schema/blob/main/docs/overview/Index.md)
- [Agnostic Data Labs (ADL) Documentation](https://docs.agnosticdatalabs.com/docs/)
- [ADL Schema Reference](https://docs.agnosticdatalabs.com/docs/schema-reference/dwa-model/)
- [Event-based orchestration pattern](../data-engineering-design-patterns/design-patterns/event-based-orchestration.md)
- [Implementation plan (Airflow + Kafka)](plan3.md)
- [WFS Extractor README](Extractors/wfs/README.md)
