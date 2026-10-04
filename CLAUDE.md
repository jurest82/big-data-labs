# CLAUDE.md: Big Data Labs

## What this repository is

Hands-on labs for **SI7006 Storage and Processing of Big Data** (EAFIT, master's program in Data Science and Analytics). Each lab accompanies a block of the course presentations: students run it during the session, in their own AWS account when the lab uses AWS, and tear everything down when they finish.

The first labs (the first weekend) use an online store as their example, with orders, customers, products, reviews (JSON), product photos and click events. There is no single running example for the whole course: the labs of later weeks may use a different context, so do not assume the store when building them. Everything in this repository is written in English: code, documentation, lab statements, and the data itself (table and column names included).

## How to work in this repository

Nothing from this project is installed directly on the host. Everything (the `aws` CLI, the `serverless` CLI, Python, formatting and linting) runs inside the Docker containers defined in `.docker/docker-compose.yml`, through the dev container at the repository root.

**Claude never runs deploys, `git push`, `serverless deploy` or `serverless remove`, or any other command that changes state in AWS or in the repository's remote.** Give the command, or a read-only diagnosis (`serverless print`/`package`, `aws ... describe-*`/`get-*`/`list-*`, `cfn-lint`), and let the developer run it.

One lab is built at a time. The developer reviews each lab before the next one starts.

## Repository structure

- `.docker/`: the multi-stage `Dockerfile` (`img-base`, then `img-labs`), `docker-compose.yml`, and the `git.sh`, `aws.sh` and `entrypoint.sh` scripts the dev container runs on creation. The compose file also starts a local PostgreSQL and pgAdmin (lab 1).
- `.envs/`: git-ignored credentials, `aws.env` and `sls.env`, copied from the `*.example` files. They are optional: lab 1 runs without them.
- `labs/`: one folder per lab, `labs/<NN>-<name>/`. Shared code, such as the data generator, lives in `labs/shared/`.
- Each lab folder has a `README.md` with the statement and the steps, plus its SQL, Python or `serverless.yml` files.

## The labs

| Lab | Topic                                                          | Runs on          |
| --- | -------------------------------------------------------------- | ---------------- |
| 1A  | OLTP anomalies, normalization and JOINs                        | Local PostgreSQL |
| 1B  | Star schema, a query by category and month, and a data mart    | Local PostgreSQL |
| 2   | Data lake: S3, a Glue crawler and Athena, plus a data swamp    | AWS              |
| 3   | Apache Iceberg table: update, schema evolution and time travel | AWS              |
| 4   | Medallion layers (bronze, silver, gold) with SQL in Athena     | AWS              |
| 5   | Streaming click events to S3 with Firehose                     | AWS              |

Labs 2 to 4 share one base stack (S3 bucket with zones, a Glue database and an Athena workgroup) deployed once with the Serverless Framework. The Firehose stack of lab 5 is separate. AWS labs use only light services (S3, Glue, Athena, Firehose); no RDS or Redshift. Everything deployed is destroyed at the end of each day. CloudFormation cannot delete a bucket that still has objects, so a destroy step empties the bucket first.

## Lab conventions

- Each lab README follows the same standard as the root `README.md`: a `# README` title with a table of contents, then Summary, Setup (the steps, each with its expected result) and Remove (how to destroy what was deployed), separated by `---`. A Glossary goes only when there is something to define, such as environment variables. A lab README does not say after which slide of the course it is done or which slides it relates to: the presentation points to the lab, not the other way around.
- Windows compatibility matters: most students use Windows and the maintainer uses macOS. `.gitattributes` forces LF line endings on every text file and `.devcontainer.json` strips any CR from `.docker/*.sh` on creation. Keep both working when adding new file types or scripts (add the extension to `.gitattributes`).
- Data and schema names are in English (`orders`, `customers`, `products`, `order_items`, `reviews`, `clicks`).
- Verify every claim about an AWS service against its official documentation before writing it into a lab. Do not answer from memory.
- Serverless Framework, CLI only, no Serverless Dashboard: no `org:` or `app:` keys in any `serverless.yml`. `SERVERLESS_ACCESS_KEY` in `.envs/sls.env` is only for CLI licensing, and each student uses their own.

## Formatting

`npm run format` runs Prettier (JSON, YAML, Markdown) and `yapf` (Python, configured in `pyproject.toml`). `npm run format:check` checks without writing. `pylint` uses the same `pyproject.toml`.

## Documentation convention

Human-facing docs (`README.md` at any level) never reference `CLAUDE.md`: it is written for the AI agent working in this repository, not for people reading the project's documentation.

## Commit convention

Base: Conventional Commits: types like `feat`/`fix`/`refactor`/`chore`/`docs`/`test`, imperative mood, no trailing period.

Each line of the message is a bullet `* <type>: <description>` (with a literal `*` at the start), one line per distinct change, even if several land in the same commit. No separate body, no additional explanation below the bullets. Example:

```text
* feat: add the local PostgreSQL and pgAdmin services
* chore: add Prettier, yapf and markdownlint configuration
* docs: add the lab 1A statement
```

When a commit touches several things, reflect each one in its own bullet. If the changes are very different in nature, prefer several separate commits.

**Never add Claude co-authorship to commits in this repository.**
