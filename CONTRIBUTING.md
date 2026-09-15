# Team workflow

## Updating an existing week

1. Pull the latest `main` and create a descriptive branch, such as `week-02/discussion`.
2. Edit the relevant week's files. Keep original data snapshots unchanged.
3. If Stata code changes, rerun that week's do-file and inspect its generated results.
4. If the report changes, rebuild it, check the rendered PDF, and include it in the same pull request.
5. Open a pull request describing the change and validation. Ask a teammate to review it.

## Adding a week

Create a `week-NN/` directory containing a README, do-file(s), `data/` and `output/` as needed. Document the task, data source and date, commands to run, and deliverables. Add the week to the root README index. Add a root runner when useful.

## File conventions

- Use relative paths and document the expected working directory.
- Track final reports, tables and figures so teammates can review without rerunning Stata.
- Keep temporary files, logs, credentials and personal machine paths out of commits.
- Preserve data source URLs, retrieval dates, units and sample restrictions.
- Keep statistical conclusions consistent with the generated results.
