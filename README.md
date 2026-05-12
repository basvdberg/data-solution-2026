# Data Solution 2026

This project is a proof of concept to show an implementation of a data solution using the following innovative breakthroughs that happened in 2026:

- Improve data engineering efficiency by AI-based code generation, in my case using [Cursor 3.3](https://cursor.com/changelog).
- Implement the ideas of the book *Data Engine Thinking* by Roelant Vos and Dirk Lerner ([dataenginethinking.com](https://dataenginethinking.com/)).
- Use the open-source [Data Solution Automation (DSA) metadata schema](https://github.com/data-solution-automation-engine/data-warehouse-automation-metadata-schema) as the standard format for source-to-target mappings, data objects, and connections.
- Use [Agnostic Data Labs (ADL)](https://docs.agnosticdatalabs.com/docs/) to visualize DSA schemas and to generate code from Handlebars templates.
- Implement the data engineering design patterns described in the companion repo [data-engineering-design-patterns](../data-engineering-design-patterns/).

## Project layout

```text
data-solution-2026/
├── Classifications/         Tag-based labels applied to data objects
├── Configurations/          Project-level ADL configuration
├── Connections/             Data connection definitions (sources, targets)
│   └── Sources/
├── Conventions/             Naming conventions and standards
├── Data/                    Extracted data landing zone (gitignored)
│   └── 000_Source/          Raw Parquet files from source extractors
├── DataObjects/             Table / view / query definitions (one JSON per object)
│   ├── 000_Source/          Source system table definitions
│   ├── 100_Landing_Area/    Landing area table definitions
│   └── 150_Persistent_Staging_Area/
├── DataObjectMappings/      Source-to-target mappings + extractor configs
│   ├── Staging/             Landing area mappings
│   └── PersistentStaging/   PSA mappings
├── Extractors/              Runtime extraction logic (Python), by protocol
│   ├── common/              Shared utilities (config loader, Parquet writer)
│   ├── odata/               OData v4 HTTP client + CLI driver
│   └── wfs/                 OGC WFS 2.0 client + GML parser + CLI driver
├── Output/                  Generated artefacts (SQL, scripts, docs)
├── Perspectives/            Custom views / filters over the metadata
├── Schemas/                 JSON Schema definitions for the metadata format
├── Settings/                ADL application settings
└── Templates/               Handlebars templates for code generation
    ├── DataObjectMappingLists/   Stored procedure templates (landing, PSA)
    ├── DataObjects/              DDL templates (source, landing, PSA tables)
    └── Other/                    Deployment, documentation, sample data
```

## Getting started

### Prerequisites

- Python 3.10+
- [ADL](https://docs.agnosticdatalabs.com/docs/) for metadata management and code generation

### Install Python dependencies

```powershell
pip install -r Extractors/requirements.txt
```

### Run an extractor

From the project root:

```powershell
# OData: smoke test against the public Northwind v4 reference service
python -m Extractors.odata --config DataObjectMappings/odata-demo.json --mapping odata-demo-regions

# OData: extract CBS (Dutch statistics) dataset (requires network access to datasets.cbs.nl)
python -m Extractors.odata --mapping cbs-84583NED --limit 5000

# WFS: extract KNMI daily temperature observations (2 stations, capped at 100 records)
python -m Extractors.wfs --mapping knmi-daggegevens-temperature --page-size 2 --max-features 2 --limit 100
```

Output lands under `Data/000_Source/...` as defined by the `landing_path_template`
extension in each mapping JSON.

## Available data sources

| Source | Protocol | Config | Description |
| --- | --- | --- | --- |
| CBS 84583NED | OData v4 | `DataObjectMappings/cbs.json` | Dutch government statistics (datasets.cbs.nl) |
| Northwind | OData v4 | `DataObjectMappings/odata-demo.json` | Public reference service for smoke testing |
| KNMI daggegevens | WFS 2.0 | `DataObjectMappings/knmi-daggegevens.json` | Daily climate observations from 33 Dutch weather stations |

## Reference

- [Data Solution Automation Schema](https://github.com/data-solution-automation-engine/data-warehouse-automation-metadata-schema/blob/main/docs/overview/Index.md)
- [Agnostic Data Labs (ADL) Documentation](https://docs.agnosticdatalabs.com/docs/)
- [ADL Schema Reference](https://docs.agnosticdatalabs.com/docs/schema-reference/dwa-model/)
- [Extractors README](Extractors/README.md)
- [WFS Extractor README](Extractors/wfs/README.md)
