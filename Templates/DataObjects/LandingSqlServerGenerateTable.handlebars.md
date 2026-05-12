---
uid: LandingSqlServerGenerateTable
---

# Landing Area Generate Table

## Purpose

This code-generation template creates table creation scripts for SQL Server based on Landing Area conventions. 

## Motivation

After importing data definitions from operational ('source') systems, a typical next step is generating corresponding Landing Area objects to load the data delta into. This template creates these tables, using the operational system data object definition as input.

## Applicability

* SQL Server family databases

### Design Pattern

* [Staging / Landing](https://github.com/data-solution-automation-engine/data-solution-framework/blob/main/design-patterns/design-pattern-staging-layer-landing-area.md)

### Schema Type

* [Data Object](xref:DataWarehouseAutomation.DataObject)

### Output Type

* [Data Definition Language (DDL)](xref:output-type-data-definition-language)

## Implementation guidelines

This template is intended to be assigned to 'source' Data Objects. It will add the defined data solution standard columns and streamline the data types.

### Considerations and consequences

> [!NOTE]
> Character columns that are part of the Primary Key definition will be generated with character length 100.
> This is because these columns are used in various window functions and indexes, which are subject to size / length limitations in SQL Server.

### Extensions

N/A.

