# Schema follow-ups

## Table of contents

<!-- markdown-toc:start -->
- [1. Data types](#1-data-types)
- [2. Classifications](#2-classifications)
- [3. Extensions](#3-extensions)
- [4. Cross-cutting](#4-cross-cutting)
- [Suggested order of attack](#suggested-order-of-attack)
<!-- markdown-toc:end -->

Open items for `data-objects.schema.json`. The schema is intentionally permissive today (free-form strings, custom fields allowed) so we can iterate on the controlled vocabularies separately from the structural skeleton. One Data Object is stored per file; the schema root is a single Data Object.

## 1. Data types

Status: `dataItem.dataType` is a free-form string. Sample uses `int` and `date`.

Goals:

- Decide on a **logical type system** that is technology-agnostic, plus a mapping to physical types per target engine.
- Decide which length / precision / scale fields are mandatory per type.
- Enforce the vocabulary in the schema with an `enum` (or `oneOf` of `const`s + `description`s for tooling).

Proposed logical types (first pass, to validate):

| Logical type | Notes | Length | Precision | Scale |
|---|---|---|---|---|
| `string` | Variable-length text | required | – | – |
| `char` | Fixed-length text | required | – | – |
| `int` | 32-bit integer | – | – | – |
| `bigint` | 64-bit integer | – | – | – |
| `smallint` | 16-bit integer | – | – | – |
| `decimal` | Exact numeric | – | required | required |
| `float` | Approximate numeric | – | – | – |
| `boolean` | True/false | – | – | – |
| `date` | Calendar date, no time | – | – | – |
| `time` | Time of day | – | – | optional |
| `datetime` | Local date+time | – | – | optional |
| `timestamp` | Date+time with timezone | – | – | optional |
| `binary` | Byte array | optional | – | – |
| `json` | Structured JSON value | – | – | – |
| `uuid` | UUID identifier | – | – | – |

Concrete tasks:

- [ ] Confirm the logical type list above (add/remove).
- [ ] Decide whether `dataType` should be an `enum` (strict) or just documented (loose). Recommend strict.
- [ ] In `dataItem`, add JSON Schema `if/then` clauses to require `characterLength` for `string`/`char` and `numericPrecision`+`numericScale` for `decimal`.
- [ ] Author a separate `dataTypeMappings.json` per engine: `MSSQLDB`, `Snowflake`, `Databricks`, `Postgres`. (Out of band of this schema, consumed by the code generator.)
- [ ] Decide nullability: add a `isNullable` boolean to `dataItem` (today it's implicit).

Open questions:

- Do we need precision-aware integer types (`tinyint`, `smallint`, `bigint`) or is `int` + range hints enough?
- How do we model `datetime` precision across engines (e.g. `datetime2(7)`)?

## 2. Classifications

Status: `classification` accepts any `group` + `classification` string. Sample uses `Solution Layer` and `Solution Area` groups.

Goals:

- Define which **groups** are well-known, and the **allowed values** within each.
- Decide whether unknown groups are allowed (extensibility vs strictness).
- Use JSON Schema `oneOf` + `const` per group to validate group↔classification pairs.

Proposed groups and values (first pass):

| Group | Allowed classifications |
|---|---|
| `Solution Layer` | `Operational System`, `Landing`, `Persistent Staging`, `Raw Data Vault`, `Business Data Vault`, `Information Mart`, `Helper` |
| `Solution Area` | `Operational System`, `Subject Area`, `Conformed`, `Sandbox` |
| `Data Sensitivity` | `Public`, `Internal`, `Confidential`, `Restricted`, `PII` |
| `Object Type` | `Hub`, `Link`, `Satellite`, `Reference`, `Dimension`, `Fact`, `Bridge` |
| `Lifecycle` | `Active`, `Deprecated`, `Retired` |

Concrete tasks:

- [ ] Agree on the group list and values above.
- [ ] In the schema, model `classification` as a `oneOf` over groups, each branch fixing `group` to a `const` and `classification` to an `enum`.
- [ ] Decide if `group` is required (today it's optional). Recommend required for new content.
- [ ] Move classification text from `notes` into a structured `description` registry (so notes stay free-form for instance-level remarks).
- [ ] Decide whether to allow multiple values per group on the same object (yes for `Data Sensitivity`? no for `Solution Layer`?).

Open questions:

- Should "Solution Layer" influence which `templateMappings` are valid (e.g. `Persistent Staging` ⇒ requires the PSA template)?

## 3. Extensions

Status: `extension.key` is a free-form string. Sample uses `location`, `connectionString`, `connectionType`, `datastore`, `originatingSystem`.

Goals:

- Define a registry of **well-known keys** and their expected shape / values.
- For connection-typed objects, require the right keys to be present.
- Keep the door open for custom keys (no `additionalProperties: false`).

Proposed well-known keys:

| Key | Applies to | Value | Notes |
|---|---|---|---|
| `location` | `dataConnection` | string | Schema / namespace within the database |
| `connectionString` | `dataConnection` | string | Provider-specific connection string |
| `connectionType` | `dataConnection` | enum: `MSSQLDB`, `Snowflake`, `Databricks`, `Postgres`, `FlatFile`, `BlobStorage`, `S3` | Drives downstream codegen |
| `datastore` | `dataConnection` | string | Database / catalog name |
| `originatingSystem` | `dataObject` | string | Source system code (e.g. `SAVEMORE`) |
| `loadStrategy` | `dataObject` | enum: `Full`, `Delta`, `Cdc`, `Snapshot` | How the object is loaded |
| `effectiveDateColumn` | `dataObject` | string | Name of a column used as effective-from |
| `recordSource` | `dataObject` | string | Record source code for Data Vault |

Concrete tasks:

- [ ] Confirm the key list above.
- [ ] Add a `definitions/knownExtensionKey` enum and warn (but not fail) on unknown keys via tooling. The schema stays open, but a separate "linting" pass enforces the registry.
- [ ] Add JSON Schema `if/then`:
    - if `extension.key == "connectionType"`, then `value` must be one of the enumerated connection types.
    - if `extension.key == "loadStrategy"`, then `value` must be one of the enumerated strategies.
- [ ] Decide whether key names are case-sensitive (recommend yes, camelCase).
- [ ] Validate uniqueness of `key` within an extensions array (today only the whole object must be unique).

Open questions:

- Should some of these be promoted from "extension" into **first-class properties** on `dataConnection` / `dataObject`? Candidates: `connectionType`, `loadStrategy`, `originatingSystem`. Pro: discoverability and stricter validation. Con: less flexibility for unknown consumers.

## 4. Cross-cutting

- [ ] Add a top-level `schemaVersion` (or similar) string to the Data Object root so consumers can detect schema generation. (The old "collection root" was removed when we moved to one Data Object per file.)
- [ ] Tighten `id` formats: require UUID at all `id` fields (today only the root Data Object's `id` is `format: uuid`; `dataConnection.id`, `dataItem.id`, `classification.id`, and `extension.id` are plain strings, with `dataConnection.id` and `classification.id` explicitly allowed to be empty).
- [ ] Decide on a final `$id` URL once the schema is published (currently a placeholder under `example.com`).
- [ ] Add example fixtures under `examples/` (one per `connectionType`, one Data Object per file) for documentation and regression tests.
- [ ] Set up automated validation in CI: walk `DataObjects/**/*.json` (excluding `*.schema.json`) and validate each against `data-objects.schema.json`. The script we used during authoring can be moved to `scripts/validate.py`.

## Suggested order of attack

1. Lock the **logical data type** list and add the `enum` + conditional rules.
2. Lock the **classification groups + values** and switch `classification` to a `oneOf`.
3. Add the **extension key registry** and conditional value validation.
4. Promote any "must-have" extensions to first-class properties.
5. Add CI validation and `examples/`.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
  - Classifications
  - Configurations
  - Connections
    - Sources
  - Conventions
  - Dataobjectmappings
    - 000_Source
      - Knmi
        - Roelant
    - Persistentstaging
    - Staging
  - Dataobjects
    - 000_Source
      - Dbo
    - 100_Landing_Area
      - Dbo
    - 150_Persistent_Staging_Area
      - Dbo
  - Docs
    - [Markdown automation](../docs/markdown-automation.md)
  - Extractors
    - Common
    - Odata
    - Wfs
  - Perspectives
  - Schemas
    - [Schema follow-ups](follow-ups.md)
  - Settings
  - Templates
    - Dataobjectmappinglists
      - [Landing Area Stored Procedure Delta](../Templates/DataObjectMappingLists/LandingSqlServerStoredProcedureDelta.handlebars.md)
      - [Landing Area Stored Procedure Landing](../Templates/DataObjectMappingLists/LandingSqlServerStoredProcedureLanding.handlebars.md)
      - [Persistent Staging Area Stored Procedure Delta](../Templates/DataObjectMappingLists/PersistentStagingSqlServerStoredProcedureDelta.handlebars.md)
      - [Persistent Staging Area Stored Procedure Full Outer Join](../Templates/DataObjectMappingLists/PersistentStagingSqlServerStoredProcedureFullOuterJoin.handlebars.md)
    - Dataobjects
      - [Source Area Generate Table](../Templates/DataObjects/CreatePhysicalDataObject.handlebars.md)
      - [Landing Area Generate Table](../Templates/DataObjects/LandingSqlServerGenerateTable.handlebars.md)
      - [Persistent Staging Area Generate Table](../Templates/DataObjects/PersistentStagingSqlServerGenerateTable.handlebars.md)
      - [Source Area Generate Table](../Templates/DataObjects/SourceSqlServerGenerateTable.handlebars.md)
    - Other
      - [Deployment](../Templates/Other/Container.handlebars.md)
      - [Control Framework Registration](../Templates/Other/ControlFrameworkRegistration.handlebars.md)
      - [Databases](../Templates/Other/Databases.handlebars.md)
      - [Deployment](../Templates/Other/Deployment.handlebars.md)
      - [Documentation](../Templates/Other/Documentation.handlebars.md)
      - [Readme](../Templates/Other/Readme.handlebars.md)
      - [Sample Data - SaveMore Source System](../Templates/Other/SampleDataSqlServer.handlebars.md)
  - [Phase one: CBS OData extraction with event-based orchestration](../plan1.md)
  - [Phase two: minimal Dutch government OData ingestion with event-based orchestration](../plan2.md)
  - [Phase three: JSON-configured Dutch government OData ingestion](../plan3.md)
<!-- markdown-project-structure:end -->
