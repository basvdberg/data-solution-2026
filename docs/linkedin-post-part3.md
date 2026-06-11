# LinkedIn post (part 3)

## Table of contents

<!-- markdown-toc:start -->
- [Post](#post)
<!-- markdown-toc:end -->

## Post

Lessons from building a data engineering PoC with an AI agent.

In my [May post](https://github.com/basvdberg/data-engineering-2026) I described a new way of working with GenAI. In June I shared progress on the [Data Solution 2026](https://github.com/basvdberg/data-solution-2026) proof of concept. Here is what I learned along the way.

Working with an AI agent feels like having a **junior** assistant — working really hard to help you out. I emphasize *junior* because it does require me to **fully specify** what needs to be done.

I asked it to generate code for a data object poller in Airflow, assuming it would use the latest version. It did not — it followed Airflow 2 patterns while my server runs Airflow 3. Maybe there is simply more Airflow 2 content on the internet. Either way, it caused real issues that a single line in the prompt ("we run Airflow 3.2") would have avoided.

**SSH troubleshooting ate more time than it should.** The agent runs commands on my local NAS over SSH. Non-interactive sessions had a minimal `PATH` (`docker` not found), nested quoting from PowerShell broke remote commands, and the same workarounds were rediscovered session after session. Fixing the default path for remote SSH cleared a lot of noise — but the agent will not do that by itself. You have to build it into your way of working: collect recurring issues (like a sprint review), turn fixes into skills and scripts, and enforce them in the next session.

**Learning by doing beat reading docs.** I was new to Apache Airflow and Apache Kafka. Learning from working examples in *my* architecture — with the agent as tutor — got me productive faster than documentation or YouTube alone.

**Making tacit knowledge explicit pays off.** DevOps habits, automatic deployment, testing, documenting, versioning — all of it matters more when an agent is doing the implementation. That is an upfront investment. I expect a strong return.

**What is running today:** a poller that checks a public data source every hour. When data changes, it publishes a change event to Kafka; when it does not, it logs an unchanged event. Kafka separates those event types so you can see exactly when source data moved — and trigger extraction only when something actually changed.

Full notes (infra, SSH, Airflow version mismatch, CI/CD):

- <https://github.com/basvdberg/data-solution-2026/blob/main/lessons-learned-part1.md>
- <https://github.com/basvdberg/data-solution-2026/blob/main/lessons-learned-part2.md>

#DataEngineering #GenAI #ApacheAirflow #ApacheKafka #ProofOfConcept #DataArchitecture

## Project structure

<!-- markdown-project-structure:start -->
- [Data Solution 2026](../readme.md)
  - Docs
    - [LinkedIn post (part 3)](linkedin-post-part3.md)
- Related repositories
  - [Data Engineering 2026](https://github.com/basvdberg/data-engineering-2026) — Course and learning materials
  - [Data Engineering Design Patterns](https://github.com/basvdberg/data-engineering-design-patterns) — Design pattern catalogue
<!-- markdown-project-structure:end -->
