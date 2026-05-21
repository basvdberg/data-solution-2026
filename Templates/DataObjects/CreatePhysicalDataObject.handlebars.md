## Table of contents

<!-- markdown-toc:start -->
- [Purpose](#purpose)
- [Motivation](#motivation)
- [Applicability](#applicability)
  - [Design Pattern](#design-pattern)
  - [Schema Type](#schema-type)
  - [Output Type](#output-type)
- [Implementation guidelines](#implementation-guidelines)
  - [Considerations and consequences](#considerations-and-consequences)
  - [Extensions](#extensions)
<!-- markdown-toc:end -->

## Table of contents


---
uid: CreateView
---

# Source Area Generate Table

## Purpose

This code-generation template generates a data object JSON file.

## Motivation

## Applicability

* JSON

### Design Pattern

### Schema Type

* [Data Object](xref:DataWarehouseAutomation.DataObject)

### Output Type

* [Data Definition Language (DDL)](xref:output-type-data-definition-language)

## Implementation guidelines


### Considerations and consequences

### Extensions

N/A.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../../readme.md)
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
    - [Markdown automation](../../docs/markdown-automation.md)
  - Extractors
    - Common
    - Odata
    - Wfs
  - Perspectives
  - Schemas
    - [Schema follow-ups](../../Schemas/follow-ups.md)
  - Settings
  - Templates
    - Dataobjectmappinglists
      - [Landing Area Stored Procedure Delta](../DataObjectMappingLists/LandingSqlServerStoredProcedureDelta.handlebars.md)
      - [Landing Area Stored Procedure Landing](../DataObjectMappingLists/LandingSqlServerStoredProcedureLanding.handlebars.md)
      - [Persistent Staging Area Stored Procedure Delta](../DataObjectMappingLists/PersistentStagingSqlServerStoredProcedureDelta.handlebars.md)
      - [Persistent Staging Area Stored Procedure Full Outer Join](../DataObjectMappingLists/PersistentStagingSqlServerStoredProcedureFullOuterJoin.handlebars.md)
    - Dataobjects
      - [Source Area Generate Table](CreatePhysicalDataObject.handlebars.md)
      - [Landing Area Generate Table](LandingSqlServerGenerateTable.handlebars.md)
      - [Persistent Staging Area Generate Table](PersistentStagingSqlServerGenerateTable.handlebars.md)
      - [Source Area Generate Table](SourceSqlServerGenerateTable.handlebars.md)
    - Other
      - [Deployment](../Other/Container.handlebars.md)
      - [Control Framework Registration](../Other/ControlFrameworkRegistration.handlebars.md)
      - [Databases](../Other/Databases.handlebars.md)
      - [Deployment](../Other/Deployment.handlebars.md)
      - [Documentation](../Other/Documentation.handlebars.md)
      - [Readme](../Other/Readme.handlebars.md)
      - [Sample Data - SaveMore Source System](../Other/SampleDataSqlServer.handlebars.md)
  - [Phase one: CBS OData extraction with event-based orchestration](../../plan1.md)
  - [Phase two: minimal Dutch government OData ingestion with event-based orchestration](../../plan2.md)
  - [Phase three: JSON-configured Dutch government OData ingestion](../../plan3.md)
<!-- markdown-project-structure:end -->
