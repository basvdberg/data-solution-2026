# Markdown automation

## Table of contents

<!-- markdown-toc:start -->
- [One-time setup (per clone)](#one-time-setup-per-clone)
- [Manual refresh](#manual-refresh)
- [Editing rules](#editing-rules)
<!-- markdown-toc:end -->

Every `.md` file in this repository is updated automatically with:

- a **Table of contents** at the top (built from `##`–`######` headings)
- a **Project structure** tree at the bottom (repository **folders only**, with short descriptions from `project-structure-descriptions.json`)

## One-time setup (per clone)

```powershell
..\cursor-config\scripts\setup-githooks.ps1 .
..\cursor-config\scripts\install-skills.ps1
```

That points `core.hooksPath` at [cursor-config](../cursor-config/githooks/) so pre-commit runs the shared Markdown and `prompts.md` updaters from [cursor-config](../cursor-config/).

## Manual refresh

```powershell
python ..\cursor-config\scripts\update_markdown_docs.py
python ..\cursor-config\scripts\update_markdown_docs.py --toc-only
python ..\cursor-config\scripts\update_markdown_docs.py --structure-only
```

Cursor skills are versioned in [cursor-config/skills/](../cursor-config/skills/) and linked into `~/.cursor/skills/` by `install-skills.ps1`.

## Editing rules

Do not edit content between these markers by hand; the hook will overwrite it:

- ``
- ``

Edit the main body of the document outside those blocks.

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
    - [Markdown automation](markdown-automation.md)
  - Extractors
    - Common
    - Odata
    - Wfs
  - Perspectives
  - Schemas
    - [Schema follow-ups](../Schemas/follow-ups.md)
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
- Related repositories
  - [cursor-config](https://github.com/basvdberg/cursor-config)
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026)
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns)
<!-- markdown-project-structure:end -->
