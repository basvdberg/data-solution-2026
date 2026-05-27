# Extractor and poller

## Table of contents

<!-- markdown-toc:start -->
_No sections yet._
<!-- markdown-toc:end -->

Open-Meteo extractor and poller driven by `data-object-mapping/` JSON.

Run from the solution root (`data-solution-2026/`):

```powershell
python -m extractor_and_poller.poller --list
python -m extractor_and_poller.poller --mapping daily-temperature
python -m extractor_and_poller.openmeteo.extractor --mapping daily-temperature
```

The `openmeteo/` subfolder holds the `extractor/` and `poller/` packages. Shared helpers live under `common/`; the generic poller CLI is in `poller/`.

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
  - Classification
  - Configuration
  - Connection
  - Convention
  - Data
    - Staging
      - Openmeteo
        - Daily_Temperature
  - Data Object
    - Source
      - Openmeteo
    - Staging
      - Openmeteo
  - Data Object Mapping
    - Staging
      - Openmeteo
  - Doc
    - Data Object Mapping
    - [Remote SSH development workflow](../doc/remote-ssh.md)
  - Extractor_And_Poller
    - Common
    - Openmeteo
      - Extractor
      - Poller
    - Poller
    - Tests
  - Output
  - Perspective
  - Schema
    - [Schema follow-ups](../schema/data-objects-schema.md)
  - Setting
  - Template
  - [DSA interface](../dsa-interface.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026)
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns)
<!-- markdown-project-structure:end -->
