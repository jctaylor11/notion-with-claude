---
name: setup
description: Builds the Notion workspace that the notes and learnings skills file into. Only the user runs it, as /notion-workspace:setup; the other skills send them here when config.json is missing.
disable-model-invocation: true
---

# Set up the Notion workspace

Creates the databases listed in `${CLAUDE_PLUGIN_ROOT}/schema/databases.json` under the user's workspace page, and records their IDs in `${CLAUDE_PLUGIN_DATA}/config.json`. Safe to re-run: it only creates what's missing and never edits or deletes anything that exists.

Use the `notion-write-test` tools for every write and the `notion-read-test` tools for every read. If a step needs a tool that isn't available, or a write target outside the workspace page, stop and tell the user. Never call the Notion API another way.

## 1. Find the workspace page

The write token can only see pages the user shared with it, so the workspace page is the one it can see, whatever the user named it.

1. Search with `notion-write-test` `post-search`, filtered to pages.
2. Keep results whose parent page is not itself in the results. Those are the shared top-level pages.
3. If exactly one remains, tell the user its title and carry on. If none, stop: ask them to share the page with the write integration. If several, stop and ask which one is the workspace.

## 2. Load existing config

Read `${CLAUDE_PLUGIN_DATA}/config.json`. If it's missing, start from an empty one. If it names a different workspace page than step 1 found, stop and ask.

## 3. Create the databases

For each database in the schema, in order:

1. List the workspace page's children (`get-block-children`) and look for a `child_database` with the same title. If one exists, record its IDs in the config as already there, and move on without changing it.
2. Otherwise call `create-database` with the workspace page as parent, the schema's `title`, `icon` and `description`, and its `properties` as `initial_data_source.properties`.
3. Take `database_id` and `data_source_id` from the response and write both to `config.json` straight away, so a failed run resumes where it stopped.

Config shape:

```json
{
  "workspace_page_id": "…",
  "databases": {
    "library": { "database_id": "…", "data_source_id": "…" }
  }
}
```

## 4. Report

Say what was created, what was already there and what failed, one line each, with a link to each created database. Don't describe the schema back to the user.
