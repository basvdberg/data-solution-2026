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
uid: PersistentStagingSqlServerGenerateTable
---

# Persistent Staging Area Generate Table

## Purpose

This code-generation template creates table creation scripts for SQL Server based on Persistent Staging Area (PSA) conventions. 

## Motivation

PSA tables typically follow the structure of the operational data systems to which the data solution interfaces. The PSA object contains a number of standard columns, which will be added to the definition by this template.

## Applicability

* SQL Server family databases

### Design Pattern

* [Persistent Staging Area (PSA)](https://github.com/data-solution-automation-engine/data-solution-framework/blob/main/design-patterns/design-pattern-staging-layer-persistent-staging-area.md)

### Schema Type

* [Data Object](xref:DataWarehouseAutomation.DataObject)

### Output Type

* [Data Definition Language (DDL)](xref:output-type-data-definition-language)

## Implementation guidelines

This template is intended to be assigned to 'source' Data Objects. It will add the defined data solution standard columns and streamline the data types.

The columns that have been defined to be part of the Primary Key will be generated as NOT NULL so that constraints on the key can be enforced. The Primary Key constrains is also generated as part of this template.

### Considerations and consequences

> [!NOTE]
> Character columns that are part of the Primary Key definition will be generated with character length 100.
> This is because these columns are used in various window functions and indexes, which are subject to size / length limitations in SQL Server.

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
