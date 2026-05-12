---
uid: LandingSqlServerStoredProcedureDelta
---

# Landing Area Stored Procedure Delta

## Purpose

This code-generation template uses a Full Outer Join (FOJ / full comparison) between a source data set, and the Persistent Staging Area (PSA) to derive a data differential (delta). The detected data changes will be inserted into the staging / landing area.

## Motivation

Getting data into the data solution is often one of the hardest features to implement. This is due to the great variety of possible data sources (systems, APIs, technologies), compounded by company-specific limitations, policies, and the velocity, veracity and volume of the data itself.

A FOJ mechanism to detect changes in data is one of many ways to do so. As such, it is one of the option to consider for ingesting new data delta.

## Applicability

* SQL Server family databases; the template uses procedural SQL (T-SQL) syntax.

### Design Pattern

* [Staging / Landing](https://github.com/data-solution-automation-engine/data-solution-framework/blob/main/design-patterns/design-pattern-staging-layer-landing-area.md)

### Schema Type

* [Data Object Mapping](xref:DataWarehouseAutomation.DataObjectMappingList)

### Output Type

* [Stored Procedure](xref:output-type-stored-procedure)

## Implementation guidelines

This template requires a dedicated, transient, staging (landing) area. As part of the procedure it generates, the template will truncate the target data object -the staging area object.

It will then load the identified data delta into the staging object by comparing the latest received Persistent Staging Area (PSA) data with the latest state (most current) of data in the source object.

### Considerations and consequences

* The template requires both the source and target databases to be accessible, either via a Linked Server, on-premises cross-database query feature, or because the source- and target data sets are located in the same database.
* This pattern has limited scalability, and is best applied for smaller data sets.
* A Full Outer Join mechanism will only detect data changes at runtime. If data has changed multiple times, only the state as per when the comparison is run will be detected.

### Extensions

* [Has Control Framework](xref:has-control-framework)

