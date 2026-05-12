---
uid: PersistentStagingSqlServerStoredProcedureDelta
---

# Persistent Staging Area Stored Procedure Delta

## Purpose

This code-generation template moves data delta from the staging / landing object into the Persistent Staging Area (PSA). The template expects the data delta to already be available in the landing object, e.g. the CDC processing must be implemented there for this template to work as expected.

The generated process will perform a left-join to prevent any data to be accidentally inserted more than once - which would lead to a constraint violation.

## Motivation

The PSA, when made part of the solution architecture, is a foundational feature of the data solution. The role as 'transaction log' of all data transactions that have been presented to the data solution requires a number of considerations, including prevention of record redundancy and ability to process all data, at all times.

The intent for this template is to be able to run the PSA process it generates continuously, or as part of a (micro) batch, but without any further dependencies.

## Applicability

* SQL Server family databases; the template uses procedural SQL (T-SQL) syntax.

### Design Pattern

* [Persistent Staging Area (PSA)](https://github.com/data-solution-automation-engine/data-solution-framework/blob/main/design-patterns/design-pattern-staging-layer-persistent-staging-area.md)

### Schema Type

* [Data Object Mapping](xref:DataWarehouseAutomation.DataObjectMappingList)

### Output Type

* [Stored Procedure](xref:output-type-stored-procedure)

## Implementation guidelines

This template supports idempotence and re-runnability by implementing two lookups (left outer joins).

The first join will check the 'oldest' record in the incoming data set against the 'most recently arrived' record in the PSA. If these records are the same, the record is omitted. If not, the records are inserted. Any subsequent records have already been identified as change records, and will be inserted into the PSA directly.

The second join will ensure that the data has not been loaded before, for example by running the same process more than once. Assuming a inscription timestamp is set on arrival, and made part of the PSA key, it is conceptually not possible to have multiple changes on the same point in time.

This PSA template detects this, so that it is possible to load, and re-load, all data at all times without encountering constraint violations.

### Considerations and consequences

* The template requires both the source and target databases to be accessible, either via a Linked Server, on-premises cross-database query feature, or because the source- and target data sets are located in the same database.
* The template requires a prior process to have determined the data delta. It does not perform any CDC itself.

### Extensions

* [Has Control Framework](xref:has-control-framework)

