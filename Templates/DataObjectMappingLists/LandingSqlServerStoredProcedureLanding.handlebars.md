---
uid: LandingSqlServerStoredProcedureLanding
---

# Landing Area Stored Procedure Landing

## Purpose

This code-generation template copies all data from the source object into the staging/landing object. No change data capture (CDC) or any form of detecting data differential is implemented in this template. The purpose is to get the data into the data solution environment for further processing, including detection of any data changes.

## Motivation

Getting data into the data solution is often one of the hardest features to implement. This is due to the great variety of possible data sources (systems, APIs, technologies), compounded by company-specific limitations, policies, and the velocity, veracity and volume of the data itself.

In some cases, the only reliable way to detect data changes is to apply a Full Outer Join (FOJ) mechanism to detect changes. This may not be possible to run against the source data object directly - for a wide range of reasons. As an alternative, data can be copied into the landing object using this template and processed further within the data solution platform.

## Applicability

* SQL Server family databases; the template uses procedural SQL (T-SQL) syntax.

### Design Pattern

* [Staging / Landing](https://github.com/data-solution-automation-engine/data-solution-framework/blob/main/design-patterns/design-pattern-staging-layer-landing-area.md)

### Schema Type

* [Data Object Mapping](xref:DataWarehouseAutomation.DataObjectMappingList)

### Output Type

* [Stored Procedure](xref:output-type-stored-procedure)

## Implementation guidelines

This template requires a dedicated, transient, staging (landing) area. As part of the procedure it generates, the template will truncate the target data object -the Landing Area object- and load all data into the staging object.

### Considerations and consequences

* The template requires both the source and target databases to be accessible, either via a Linked Server, on-premises cross-database query feature, or because the source- and target data sets are located in the same database.
* This pattern has limited scalability, and is best applied for smaller data sets.
* Subsequent data delta / differential detection is recommended downstream, to be able to detect logical deletes.

### Extensions

* [Has Control Framework](xref:has-control-framework)

