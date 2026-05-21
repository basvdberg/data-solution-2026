# Prompts

This document contains the prompts used to generate and refine the content in **data-solution-2026**.

## Session 1

1. Show me all datasets that you can extract using the WFS extractor, with, if possible, a description.

2. Change the source system name of point time series observation to KNMI and change the table name into dagegevens_temperature.Update folder structure under data. Add data items to knmi JSON file using the above found columns. Try to include all descriptions that you found above.

3. Make sure that Data Object mapping is using the same folder structure as data, so the KNMI mapping should fall under 0000_source/knmi.

4. Do the same for Northwind.

5. The name of the Northwind table should be regions and not odata-demo.

6. Run the KNMI extractor.

7. Create a new Markdown file called Data Solution 2026 with a purpose paragraph : this is a proof of concept to show how you can use gen-AI in building a data solution.When generating code by AI agents, it's important to stay in control. This new way of working requires us to document and define what we want to do even more than before.

## Session 2

1. @knmi-daggegevens.json Validate this JSON using the following schema and also include the schema reference in the JSON.https://github.com/data-solution-automation-engine/data-solution-automation-metadata-schema/blob/main/GenericInterface/interfaceDataSolutionAutomationMetadataV2_1.json

2. @knmi-daggegevens.json works well in a visualiser, but 

@knmi-daggegevens-gen.json does not. Could you look at the differences and propose changes that will fix this?

## Session 3

1. @data-solution-2026/Data/000_Source/KNMI/daggegevens_temperature/2026-05-12.parquet The period Begin data items seems to be incorrect since it refers to 1951. Could you troubleshoot the extractor to see if there might be a bug in the implementation? Could you show me the raw data as it comes from the source?

2. Create a new concept version of this README file that is much simpler than the current version.
- Simplify by removing CBS OData and Northwind demo.
- Replace Mermaid diagrams by a better, simplified high-level architectural diagram.
- Focus on only implementing a proof concept for the staging layer using Airflow and Kafka, and, of course, the agnostic data labs and DSA metadata schema and data engineering design patterns.Merge the Architecture paragraph with the Orchestrated Ingestion paragraph.

3. Create a new concept version of this README file that is much simpler than the current version.
- Simplify by removing CBS OData and Northwind demo.
- Replace Mermaid diagrams by a better, simplified high-level architectural diagram.
- The purpose and summary should say the same, but implementation should Focus on implementing a proof concept for the staging layer using Airflow and Kafka, and, of course, the agnostic data labs and DSA metadata schema and data engineering design patterns.Merge the Architecture paragraph with the Orchestrated Ingestion paragraph.

## Session 4

1. Create a plan for implementing a sample implementation using data engineering design patterns, based on free data ( e.g. OData). How can we trigger a refresh of this data for example?

2. create a phase one implementation plan that is scoped on extracting the data from OData using event-based orchestration. Make sure that there is a strict separation between configuration and generic code. For example, the events and scheduling and triggering should all be configured using meta data.

3. move phase-one-cbs-odata-extraction to DataEngineeringIn2026 folder. rename to plan1

## Session 5

1. Create a sample implementation of the event-based orchestration design pattern based on Free OData Data from  the dutch government using Apache Airflow and Kafka. Make sure that the data is automtically fetched daily only when changed. Use PostgressSQL to implement the Object-Property tree design pattern to store all configuration. Keep strict separation of code versus configuration. Try to make the implementation as simple as possible. Start by creating a document called plan2.md. Create rollout plan in steps.

## Session 6

1. Explain this schema:
https://github.com/data-solution-automation-engine/data-warehouse-automation-metadata-schema/blob/main/GenericInterface/interfaceDataWarehouseAutomationMetadataV2_0.json  
The related doc is here:https://github.com/data-solution-automation-engine/data-warehouse-automation-metadata-schema/blob/main/docs/overview/Index.md 
My question is: why does it say "required": [
    "dataObjectMappings"
  ],
while the documentation speaks about dataObject ? 

does this json follow the schema? Does it validate?
@DataEngineeringIn2026/sample.json

## Session 7

1. Run the WFS extractor.

## Session 8

1. kafka is running on basnas on port 9092, airflow is running on same server on port 8081. Implement plan3 the first step, which consists of extracting a dataset from OData site.

2. Create an extractor folder. For each extractor subtype, create a sub-folder, and specifically for the following website, create an extractor.https://haleconnect.com/ows/services/org.874.cb9ca55e-f4e7-4bd8-a02e-75d528e22118_wfs/org.874.794fa9da-8bf0-4053-83d8-1174f2317dcb?SERVICE=WFS&Request=GetCapabilities

3. According to my knowledge WFS does support pagination via startIndex

4. According to my knowledge WFS does support pagination via startIndex

5. Move the WFS extractor logic to the following folder data-engineering-design-patterns\implementation\full-data-solution\adl\Extractors  and move the @data-engineering-design-patterns/implementation/full-data-solution/dutch-odata-json/config/knmi-daggegevens.jsonfile into the data object mapping subfolder.

6. Create a README that explains the extractors folder and another readme specifically for the WFS extractor.

7. Data should go to the Data folder with a capital D under ADL. Please try to get rid of the Scripts folder and move the code to the corresponding Extractors.

8. Option two. And create a new project from the implementation subfolder. Rename this into data solution 2026.

9. check and finish @data-solution-2026/README.md

10. Synchronize the folder structure under data to be identical to data objects.So bronze should become 000_source.

11. Synchronize the folder structure under data to be identical to data objects.So bronze should become 000_source.

12. Omit the extractor name in the folder naming under data. Specifically, remove odata demo.
