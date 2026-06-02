# Prompts used in v2026.06.02.1

Collected from project prompt history and release work context.

## Primary prompts

1. Create an implementation plan to set up the poller using the Airflow user interface.
2. Give me the first steps of the plan. Use openMeta data object poller implementation in this project. Use connections as defined in the connection.
3. For step one, I need to deploy my solution to my server, create a CI/CD plan using versioning and release notes.
4. Create Release Folder. Populate this with release notes and also set up versioning. Merge above plan with the existing plan under doc/design/ci-cd, but remove the need to create a feature branch. Keep it simple. Just work on the main branch, and also I would like to automatically deploy when committing to main.
5. @data-solution-2026/doc/design/ci-cd.md is still mentioning a feature branch.
6. GitHub has no access to my local server. adjust the deploy plan accordingly.
7. Can we also schedule a pull of main from this development cursor environment on committing? This would need to invoke a script that tries to pull for a certain amount of time and wait for the commits to complete and the CI actions also.
8. Yes, use a post-push hook. Also, I would like to get notified on success or failure. What's the best way to do this?
9. use ntfy.

## Source references

- Project prompt history: [`prompts.md`](../../../prompts.md)
- Release note baseline: [`release/notes/v2026.06.02.1.md`](../../notes/v2026.06.02.1.md)
