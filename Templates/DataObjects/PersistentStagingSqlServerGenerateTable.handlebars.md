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

