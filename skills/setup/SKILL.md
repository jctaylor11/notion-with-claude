---
name: setup
description: Builds the Notion workspace that the notes and learnings skills file into. Only the user runs it, as /notion-workspace:setup; the other skills send them here when config.json is missing.
disable-model-invocation: true
---

# Set up the Notion workspace

Creates the databases listed in `${CLAUDE_PLUGIN_ROOT}/schema/databases.json` under the user's workspace page, then their relations, views (`views.json`) and front page (`workspace-page.md`), and records the database IDs in `${CLAUDE_PLUGIN_DATA}/config.json`. Safe to re-run: it only creates what's missing and never edits or deletes anything that exists.

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
  "schema_version": 1,
  "workspace_page_id": "…",
  "databases": {
    "explore": { "database_id": "…", "data_source_id": "…" },
    "library": { "database_id": "…", "data_source_id": "…" },
    "topics": { "database_id": "…", "data_source_id": "…" },
    "learnings": { "database_id": "…", "data_source_id": "…" },
    "projects": { "database_id": "…", "data_source_id": "…" }
  }
}
```

Remember each created database's `properties` map from the response (name → property ID); step 5 needs it.

## 4. Add the relations

Only after every database exists (skip any relation whose `from` or `to` database failed, and report it). For each entry in `relations`:

1. Retrieve the `from` data source. If it already has a property with that name, count it as already there and move on.
2. Otherwise call `update-a-data-source` on `from`, adding the property as `{"relation": {"data_source_id": <to's data_source_id>, "dual_property": {}}}`.
3. Retrieve the `to` data source and find the new synced property (the relation pointing back at `from`). If its name isn't `synced_property`, rename it with `update-a-data-source` on `to`.

## 5. Create the views

Only for databases created in step 3 of this run, because there is no way to list or update views. For each entry in `views.json` for that database, call `create-view` with the database and data source IDs, `name`, `type`, `filter` and `sorts`. For a board, add `configuration` `{"type": "board", "group_by": {"type": "select", "property_id": <ID of the group_by property>}}`, taking the ID from step 3.

## 6. Write the front page

Only if the workspace page holds nothing but databases (no paragraphs, headings or lists), so a page the user wrote is never touched. Read the page with `retrieve-page-markdown` to see how it writes its `<database>` tags, then call `update-page-markdown` with `replace_content` and the text of `schema/workspace-page.md`, replacing the `<!-- databases -->` line with one tag per database in schema order. Never set `allow_deleting_content`: if the call would delete anything, stop. Read the page back and confirm every database is still there.

## 7. Record the schema version

If nothing failed, set `schema_version` in `config.json` to the schema's value.

## 8. Report

Say what was created, what was already there and what failed, one line each, with a link to each created database. Don't describe the schema back to the user. Mention that the databases have no icons: `create-database` can't set them.
