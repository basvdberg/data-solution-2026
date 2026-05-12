---
uid: SourceSqlServerGenerateTable
---

# Source Area Generate Table

## Purpose

This code-generation template creates table creation scripts for Sql Server, exactly as per the defintion of the data object.

## Motivation

After importing data definitions from operational systems, a typical next step is generating source objects to load the data delta into. This template creates these tables. This template can also be used to generate data solution objects like for like.

## Applicability

* SQL Server family databases

### Design Pattern

* [Staging / Landing](https://github.com/data-solution-automation-engine/data-solution-framework/blob/main/design-patterns/design-pattern-staging-layer-landing-area.md)

### Schema Type

* [Data Object](xref:DataWarehouseAutomation.DataObject)

### Output Type

* [Data Definition Language (DDL)](xref:output-type-data-definition-language)

## Implementation guidelines

This template can be assigned to any data object definition.

### Considerations and consequences

> [!NOTE]
> Exactly the same structure is used as is defined in the data object definition. E.g. no standard data solution or framework columns are added.

### Extensions

N/A.

