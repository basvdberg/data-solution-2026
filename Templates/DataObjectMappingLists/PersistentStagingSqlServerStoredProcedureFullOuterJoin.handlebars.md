---
uid: psaSqlServerStoredProcedureFullOuterJoin
---

# Persistent Staging Area Stored Procedure Full Outer Join

## Purpose

This code-generation template uses a Full Outer Join (FOJ / full comparison) between a source data set, and the Persistent Staging Area (PSA) to derive a data differential. The identified data changes are inserted directly into the PSA.

## Motivation

Getting data into the data solution is often one of the hardest features to implement. This is due to the great variety of possible data sources (systems, APIs, technologies), compounded by company-specific limitations, policies, and the velocity, veracity and volume of the data itself.

A FOJ mechanism to detect changes in data is one of many ways to do so. As such, it is one of the option to consider for ingesting new data delta.

## Applicability

* SQL Server family databases; the template uses procedural SQL (T-SQL) syntax.

### Design Pattern

* [Persistent Staging Area (PSA)](https://github.com/data-solution-automation-engine/data-solution-framework/blob/main/design-patterns/design-pattern-staging-layer-persistent-staging-area.md)

### Schema Type

* [Data Object Mapping](xref:DataWarehouseAutomation.DataObjectMappingList)

### Output Type

* [Stored Procedure](xref:output-type-stored-procedure)

## Implementation guidelines

This template can be used to skip a dedicated, transient, staging (landing) area, and insert any identified data delta directly in the PSA.

### Considerations and consequences

* The template requires both the source and target databases to be accessible, either via a Linked Server, on-premises cross-database query feature, or because the source- and target data sets are located in the same database.
* This pattern has limited scalability, and is best applied for smaller data sets.
* A Full Outer Join mechanism will only detect data changes at runtime. If data has changed multiple times, only the state as per when the comparison is run will be detected.

### Extensions

* [Has Control Framework](xref:has-control-framework)

