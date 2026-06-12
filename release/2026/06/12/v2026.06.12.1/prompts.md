# Prompts

This document contains the prompts used to generate and refine the content in **data-solution-2026**.

## Session 1

1. Remove any reference to Landing. Change object flow diagram. It should show the layered approach of this data solution, where files are extracted in the source layer and written to the staging layer.Visualize this top-down, where the source layer is at the top.Connections are less important. This is just a property.

## Session 2

1. Rewrite @data-solution-2026/doc/remote-ssh.md  Choose option A: describe how to deploy a release to your nas

2. Improve the structure of the doc folder.
- Create a folder for design. This should include @data-solution-2026/doc/architecture-staging.png , and event-based orchestration plan and CI/CD.
- Create another folder for data solution. This should contain the data object mapping folder.

## Session 3

1. Rewrite @data-solution-2026/lessons-learned.md

## Session 4

1. Show me all datasets that you can extract using the WFS extractor, with, if possible, a description.

2. Change the source system name of point time series observation to KNMI and change the table name into dagegevens_temperature.Update folder structure under data. Add data items to knmi JSON file using the above found columns. Try to include all descriptions that you found above.

3. Make sure that Data Object mapping is using the same folder structure as data, so the KNMI mapping should fall under 0000_source/knmi.

4. Do the same for Northwind.

5. The name of the Northwind table should be regions and not odata-demo.

6. Run the KNMI extractor.

7. Create a new Markdown file called Data Solution 2026 with a purpose paragraph : this is a proof of concept to show how you can use gen-AI in building a data solution.When generating code by AI agents, it's important to stay in control. This new way of working requires us to document and define what we want to do even more than before.

## Session 5

1. Do not use the legacy KNMI endpoint Because it doesn't contain actual data. I said I wanted a data source that is refreshed daily.

## Session 6

1. Update skills to deploy changes to BasNAS via the CI/CD process, meaning that I should just commit and push my changes to main, which will trigger the deploy to BasNAS.

## Session 7

1. @knmi-daggegevens.json Validate this JSON using the following schema and also include the schema reference in the JSON.https://github.com/data-solution-automation-engine/data-solution-automation-metadata-schema/blob/main/GenericInterface/interfaceDataSolutionAutomationMetadataV2_1.json

2. @knmi-daggegevens.json works well in a visualiser, but 

@knmi-daggegevens-gen.json does not. Could you look at the differences and propose changes that will fix this?

3. The link to the sibling project Data Solution 2026 is not working in GitHub. It goes to this URL.https://github.com/basvdberg/data-engineering-2026/blob/data-solution-2026

4. Add a construction icon and also the text "This project is under construction. Estimation of how complete it is: please come back later or subscribe to receive notifications . Merge with completeness indicator

5. I meant the built-in GitHub notification functionality.

6. Try to improve the under construction notice by looking at how other GitHub projects do this. I prefer to have a bigger icon at a standard location, more in the header of the document.

7. Create a new project called **cursor-config**.Move all scripts to this repo and all.git pre-commit hooks and all skills that exist in my user directory so that I have full versioning of this reference this repo where needed.

8. Check for other files that can be deleted. Also delete the.git hooks empty folders.

9. Update the prompts markdown in each project.

10. Review this linkedin post:
How is GenAI changing data engineering—not just coding faster, but how we design, document, and deliver?
I’ve started capturing that in an open repo: https://github.com/basvdberg/data-engineering-2026
The core idea: treat documentation and intent as fuel for GenAI, not paperwork you finish after go-live.

Documentation first — update design and decisions before implementation; AI drafts quickly, you review intent, then code follows.
CI/CD shifts — generated code replaces hand-written; docs become the specification that drives generation.
Specify what, not how — declarative standards (e.g. DSA metadata) and technology-agnostic design patterns reduce ambiguity so agents don’t wander.
The repo walks through this way of working (including diagrams on the old vs new data-engineering cycle), links to the Data Engineering Design Patterns collection, and points to a Data Solution 2026 proof of concept that puts the ideas into practice. This POC is in progress. I will report the lessons learned in the near future. 
#DataEngineering #GenAI #DataArchitecture #DataSolution #DesignPatterns #CodeSpecification

## Session 8

1. According to the Airflow logs, there was a successful run of my Poller, and it wrote a row to the public.Poller table in PostgreSQL. However, when I navigate to this PostgreSQL database called Data Solution 2026 on my baSNaS port 5432, I do not see a table named public.Poller.

2. Change the infrastructure to reuse the existing Postgres instance basnas_postgress and remove the data solution 2026 instance.

## Session 9

1. @data-solution-2026/Data/000_Source/KNMI/daggegevens_temperature/2026-05-12.parquet The period Begin data items seems to be incorrect since it refers to 1951. Could you troubleshoot the extractor to see if there might be a bug in the implementation? Could you show me the raw data as it comes from the source?

2. Create a new concept version of this README file that is much simpler than the current version.
- Simplify by removing CBS OData and Northwind demo.
- Replace Mermaid diagrams by a better, simplified high-level architectural diagram.
- Focus on only implementing a proof concept for the staging layer using Airflow and Kafka, and, of course, the agnostic data labs and DSA metadata schema and data engineering design patterns.Merge the Architecture paragraph with the Orchestrated Ingestion paragraph.

3. Create a new concept version of this README file that is much simpler than the current version.
- Simplify by removing CBS OData and Northwind demo.
- Replace Mermaid diagrams by a better, simplified high-level architectural diagram.
- The purpose and summary should say the same, but implementation should Focus on implementing a proof concept for the staging layer using Airflow and Kafka, and, of course, the agnostic data labs and DSA metadata schema and data engineering design patterns.Merge the Architecture paragraph with the Orchestrated Ingestion paragraph.

## Session 10

1. Create a plan for implementing a sample implementation using data engineering design patterns, based on free data ( e.g. OData). How can we trigger a refresh of this data for example?

2. create a phase one implementation plan that is scoped on extracting the data from OData using event-based orchestration. Make sure that there is a strict separation between configuration and generic code. For example, the events and scheduling and triggering should all be configured using meta data.

3. move phase-one-cbs-odata-extraction to DataEngineeringIn2026 folder. rename to plan1

## Session 11

1. Add classification target data object. It should be staging layer Please Come up with a good protocol I'm not sure what it should be since it's a parquet file.

## Session 12

1. Create Database User for the database data-solution-2026.

2. Change data_solution into data-solution-2026 everywhere.

## Session 13

1. postgres	data-solution-2026	172.29.0.6	5432	public	"$user", public, vectors

## Session 14

1. Create a sample implementation of the event-based orchestration design pattern based on Free OData Data from  the dutch government using Apache Airflow and Kafka. Make sure that the data is automtically fetched daily only when changed. Use PostgressSQL to implement the Object-Property tree design pattern to store all configuration. Keep strict separation of code versus configuration. Try to make the implementation as simple as possible. Start by creating a document called plan2.md. Create rollout plan in steps.

## Session 15

1. Create new project called ADL feedback. Create a markdown. That Numerous Feedback First item. Yes. Issue with Loading. Generated JSON. Data object mappings

## Session 16

1. Continue the implementation of Data Solution 2026.

## Session 17

1. @data-solution-2026/doc/design/ci-cd.md is still mentioning a feature branch

## Session 18

1. Explain this schema:
https://github.com/data-solution-automation-engine/data-warehouse-automation-metadata-schema/blob/main/GenericInterface/interfaceDataWarehouseAutomationMetadataV2_0.json  
The related doc is here:https://github.com/data-solution-automation-engine/data-warehouse-automation-metadata-schema/blob/main/docs/overview/Index.md 
My question is: why does it say "required": [
    "dataObjectMappings"
  ],
while the documentation speaks about dataObject ? 

does this json follow the schema? Does it validate?
@DataEngineeringIn2026/sample.json

## Session 19

1. Create a section in the @data-solution-2026/lessons-learned-part2.md There was an issue in the CI/CD process that was caused by the fact that a path was changed in the application and also in the infrastructure, but the infrastructure was not automatically being deployed. It turns out that it's quite easy to fix these kind of issues via a chat session. This usually leads to a fix being applied, like redeploying the infrastructure; however, a better approach is to analyze whether this issue was caused by the design of the system. The issue, as it turned out, was that the CI/CD process does not deploy infrastructure changes when the infrastructure changes, so the more robust solution was to have the CI/CD process do an infra release only when infrastructure changes. On top of that, issues that occur during this proof of concept give valuable information about what goes wrong. Thus, they should be recorded per sprint or per release so that we can have a retrospective process to analyze these issues and determine whether more generic design changes need to be made or whether we need to make changes in the way of working with cursor.

## Session 20

1. Complete @data-solution-2026/lessons-learned.md  Try to fix missing hyperlinks. Try to translate Dutch to English.

## Session 21

1. Run the WFS extractor.

## Session 22

1. Create a folder Infra in Data Solution 2026 that contains all the relevant docker files.

## Session 23

1. Remove all references to @data-solution-2026/release/details/v2026.06.02.2/prompts.md  in the root.

## Session 24

1. kafka is running on basnas on port 9092, airflow is running on same server on port 8081. Implement plan3 the first step, which consists of extracting a dataset from OData site.

2. Create an extractor folder. For each extractor subtype, create a sub-folder, and specifically for the following website, create an extractor.https://haleconnect.com/ows/services/org.874.cb9ca55e-f4e7-4bd8-a02e-75d528e22118_wfs/org.874.794fa9da-8bf0-4053-83d8-1174f2317dcb?SERVICE=WFS&Request=GetCapabilities

3. According to my knowledge WFS does support pagination via startIndex

4. Move the WFS extractor logic to the following folder data-engineering-design-patterns\implementation\full-data-solution\adl\Extractors  and move the @data-engineering-design-patterns/implementation/full-data-solution/dutch-odata-json/config/knmi-daggegevens.jsonfile into the data object mapping subfolder.

5. Create a README that explains the extractors folder and another readme specifically for the WFS extractor.

6. Data should go to the Data folder with a capital D under ADL. Please try to get rid of the Scripts folder and move the code to the corresponding Extractors.

7. Option two. And create a new project from the implementation subfolder. Rename this into data solution 2026.

8. check and finish @data-solution-2026/README.md

9. Synchronize the folder structure under data to be identical to data objects.So bronze should become 000_source.

10. Omit the extractor name in the folder naming under data. Specifically, remove odata demo.

## Session 25

1. Run WFS Poller

2. help sketch a KNMI Data Platform mapping and poller rule, and add a short “stale feed” note to readme.md. replace WFS api with better and more current api

3. Run the data extractor for KNMI.

## Session 26

1. Run the KNMI Data Object Poller.

## Session 27

1. Apply the Pascal case naming convention for all folders in the Data Solution 2026 project

## Session 28

1. Restructure the extractor and poller folders. Merge them in a folder called extractor_and_poller. Each protocol should have its own subfolder, like openmeteo or wfs. In each protocol, there should be an extractor subfolder and a poller subfolder.Try to clean up unused codes.And folders.

## Session 29

1. merge @data-solution-2026/extractor_and_poller and @data-solution-2026/extractor-and-poller

2. Elaborate on the functionalities implemented in staging:
- Allow extractors to be idempotent.
- Allow decoupling mechanisms in case of network failures or issues in reading the source data.
- Implement the translation of a source data format to target data format.

3. Simplify the data solution by keeping only the open-meteo source and remove, for example, KNMI.

4. create a subfolder under Data Object Source called OpenMeteo, similar to staging. Move the Data Object @data-solution-2026/data-object/source/open-meteo.json  to the subfolder and rename this as @data-solution-2026/data-object/staging/openmeteo/daily-temperature.json  Make sure that this object has all the data items that are also present in staging OpenMeteo.

next This JSON file describes a mapping from table A to B I want you to complete the mapping according to the following example:
     "dataItemMappings": [
        {
          "id": "649cb4e1-2c01-4d28-9a5d-bbd98793ebcb",
          "name": "",
          "sourceDataItems": [
            {
              "id": "a3333333-3333-3333-3333-333333333333",
            }
          ],
          "targetDataItem": {
            "id": "b7c8d9e0-f1a2-3456-1234-789012345678",
          }
        },
