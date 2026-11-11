---
name: notes
description: File things into Claude's own workspace in Notion and keep it organised. Covers notes on a YouTube video, podcast, article, paper or course, a recap of a discussion, research, a list, a project idea or a lead to look into later. Use whenever the user sends a link to make notes on, asks to save, note or put something in Notion (including "save this project idea" and "add X to explore"), mentions something they want to look into later, or asks what they know about a topic or project from their notes.
---

# Notion workspace

The workspace page is Claude's own space in the user's Notion. Everything Claude writes to Notion goes here and stays here. Never suggest moving it into the user's own pages. Use the `notion-write-test` tools for every write, and the `notion-read-test` tools to read the rest of their Notion, and only when asked. If a tool is missing, or a write target is outside the workspace page, stop and tell the user. Never call the Notion API another way.

## State

At the start of every task, read `${CLAUDE_PLUGIN_DATA}/config.json`. If it's missing, stop and tell the user to run `/notion-workspace:setup`. It holds `workspace_page_id` and, for each database key (`explore`, `library`, `topics`, `learnings`, `projects`, plus any the tidy-up has added), its `database_id` and `data_source_id`. Wherever this skill says "the Library data source" and so on, use that ID. Never write IDs into this file.

Everything else that changes lives in the same folder: `learned-style.md` (rules learned from the user's edits) and `drafts/` (the Markdown of each note as filed, named `<page-id>.md`; create the folder if it's missing).

## Databases

**Library** (one row per item):
- Name: the source's own title, e.g. "The New Code — Sean Grove". No "Notes:" prefix.
- Type: Video, Podcast, Article, Paper, Course, Discussion, Research, List or Other.
- Topics: relation to Topics.
- Projects: relation to Projects.
- Lead: relation to To explore, for the lead this item came from, if any.
- Takeaway: one sentence.
- Status: Notes ready (Claude wrote it), Reviewed (the user has finished editing) or Done (Claude has learned from the edits).
- Source: url.
- By: "Speaker (Org) · Channel/Publication".
- Published: date.
- Added: set automatically.

**Topics** (one page per subject):
- Name.
- Summary: one line.
- Library: relation, synced automatically.
- To explore: relation, synced automatically. These are the leads on this subject.
- Updated: set automatically.
- Page body: `## Where I've got to` (a synthesis across sources) and `## Open questions`.

**Projects** (one page per thing being built or that might be built, from a passing idea to a shipped product):
- Name: short and recognisable, e.g. "Notion note-taker".
- Pitch: one sentence saying what it is and who it's for.
- Stage: Inactive (an idea, or on hold), Active (being built) or Shipped.
- Library: relation, synced automatically. It links the discussions and notes that bear on the project.
- Updated and Added: set automatically.
- Page body: `## The idea`, `## Next step` (one concrete action), `## Working docs` (once there are any), `## Decisions so far` and `## Open questions`.

**To explore** (one row per lead: something that caught the user's eye but isn't worth a deep dive yet):
- Name: what it's called, e.g. "Tracer bullets" or "The Design of Design — Fred Brooks".
- Kind: Concept, Book, Article, Video, Tool or Other.
- What it is: one factual line, enough to remember why it caught their eye. Include the user's own reason if they gave one.
- Context: one brief line on where the user came across it, in their words, e.g. "Mentioned in the Matt Pocock video about AI coding workflow". Fill it whenever they say where it came from.
- Link: the primary source, if there is one and you've confirmed it.
- Status: New, Done or Dropped.
- Topics: relation, for subjects it directly bears on.
- Library: relation, synced automatically. These are the notes made once it's explored.
- Added: set automatically.
- No page body is needed.

Topics are subjects being learned about, and Projects are things being made. A Library row can link to both.

Where project material goes:
- **The project page** holds only the overview: pitch, decisions, open questions and next step.
- **Working documents** (plans, checklists, research, draft specs) are sub-pages of the project page. List them under `## Working docs`, straight after the idea, most-used first. A new sub-page is added at the bottom of the page, so move it up.
- **Records** (notes on a source, saved discussions) are Library rows linked to the project.
- **Once the project has a code repo**, its specs, plans and task lists live in the repo as Markdown, and the project page links to them. Don't keep copies in both places.

The workspace page holds only the databases listed in `config.json`. Don't create loose pages. Anything that doesn't fit becomes a Library row with Type "Other". If a new kind of item keeps turning up, add a Type option with `update-a-data-source` rather than a new database.

Anything to read, watch or look into later goes in To explore, one row each. Don't make an empty Library row for something not yet read. A curated, ordered study plan (like the spec-driven development watch list) is different: it stays a List row in the Library.

## Filing an item

0. **Learn from reviewed notes first.** See "Learning the user's style" below.
1. **Get the full source.**
   - YouTube: `uv run ${CLAUDE_PLUGIN_ROOT}/skills/notes/scripts/fetch_youtube.py <url> <scratchpad>/transcripts`. It installs its own dependencies on first use, and prints the metadata and the transcript path. Read the whole transcript, in chunks if it's long.
   - Article, paper or web page: WebFetch, or the pdf skill for PDFs.
   - Discussion: the current conversation. Recap the decisions, the reasoning and the open questions, not the back-and-forth.
   - If you can't get the full content (no transcript, a paywall), tell the user. Never write notes from a title or blurb.
2. **Check for duplicates.** Query Library with `{"property": "Source", "url": {"equals": "<url>"}}`. If a row already exists, ask before overwriting it.
3. **Pick the topics.** Query all Topics (there are few).
   - Reuse a topic when the item is mostly about it. Use 1–2 topics per item, 3 at most.
   - Create a new topic only when nothing fits and the subject will likely come up again. Name it as a broad subject ("Evals", not "Hamel's eval talk").
   - If two topics overlap, merge them: move the relations, archive the weaker topic, and tell the user.
   - Also query Projects. Link the item to any project it bears on directly. Skip projects it only loosely relates to.
4. **Create the row.** Use `post-page` with parent `{"type": "data_source_id", "data_source_id": "<Library>"}`, every property filled in, Status "Notes ready" and an emoji icon. Then write the body with `update-page-markdown` (`replace_content`, Notion-flavoured Markdown) following `${CLAUDE_PLUGIN_ROOT}/skills/notes/style.md`, then `learned-style.md` if it exists. Learned rules win.
5. **Save the draft.** Write the exact Markdown you sent to `${CLAUDE_PLUGIN_DATA}/drafts/<page-id>.md`.
6. **Update each linked topic page.** Read it, then fold the item's key ideas into "Where I've got to".
   - Merge with existing points rather than appending. Keep 3–10 bullets, each ending with a link to its source row(s).
   - Add new open questions, and remove any this item answers.
   - Update Summary if the overall picture changed.
7. **Link it from lists.** If the item appears on a List row (e.g. a watch list), add `→ [Notes](<row url>)` after its entry.
8. **Reply briefly.** Give the row link, its topics, and one line on what changed on the topic pages. The notes themselves belong in Notion, not in chat. If any items in the notes' Resources section look worth following up, name them and offer to add them to To explore. Don't add them automatically.

## Saving a project idea

1. Query Projects first. If the idea extends an existing project, update that page instead of creating a new one.
2. Otherwise create a page with Stage "Inactive", a Pitch, and a body following the Projects template, with the first action under `## Next step`. Keep the user's own words and reasoning; don't inflate a passing idea into a plan.
3. If the idea came out of a discussion worth keeping, save that discussion to the Library too, and link the two.
4. When the user says a project has moved on (started, paused, shipped, dropped), update Stage and the `## Next step` section, and add the decision to "Decisions so far".

## Adding a lead

1. Query To explore by name first. If it's already there, say so rather than adding it twice.
2. Identify it properly. If the name is ambiguous or misremembered, find the likely match, use its correct name, and tell the user which one you assumed. Verify the facts and the link with a quick search rather than writing from memory.
3. Create the row with Status "New", plus Kind, What it is, Link and Topics where they apply.
4. A lead stays New until it's done. When it's written up, file the notes as usual with the Library row's Lead set to it, then set the lead to Done. If the user loses interest, set it to Dropped rather than deleting it.
5. When the user asks to go through their leads, list the New ones, oldest first, with their one-liners.

## Answering "what do I know about X"

Read the topic or project page first. Open linked Library rows only when you need detail, and cite them.

## Learning the user's style

Status is the queue. A note stays Notes ready until the user has finished editing it and sets it to Reviewed. At the start of each filing, or whenever the user asks you to learn from their edits:
1. Query Library for Status = Reviewed. Only these need processing. Never revisit Done rows.
2. For each row, read the page's current Markdown and compare it with `${CLAUDE_PLUGIN_DATA}/drafts/<page-id>.md`.
3. Add each meaningful change to `${CLAUDE_PLUGIN_DATA}/learned-style.md` (create it if it's missing) as one bullet stating the rule it implies. Ignore whitespace and empty blocks. If nothing changed, the note was fine as written, so add nothing.
4. Set the row's Status to Done and delete the draft. If a Reviewed row has no draft, just set it to Done.

If the user gives style feedback directly, add it to `learned-style.md` too. Learned rules override the defaults in `style.md`, which ships read-only.

## Keeping the workspace tidy

Looking after the whole workspace is part of every task that touches its structure, even when the task is narrower ("add a database", "add a property"). Don't stop at the thing that was asked for. After creating or changing a database, property or view, and before replying:

1. **Read the workspace page** (`workspace_page_id` in `config.json`) and look at it as the user would.
2. **Place it.** A new database sits with the other databases at the top, in the order the page's intro describes (lead → notes → what's learned → own learnings → what's built). New blocks are added at the bottom, so move it. Do this with `update-page-markdown` `replace_content`, keeping every existing `<database>` tag in the new order. Never set `allow_deleting_content`: if the call would delete something, stop. Afterwards, read the page back and confirm all databases are still there.
3. **Update the page's text.** Add the new thing to the intro flow, to "How it's organised" and to "Ask Claude", so the page still describes what's actually there.
4. **Record it.** Add its `database_id` and `data_source_id` to `config.json` under a short key, and put one line on how to file into it in the database's description (`update-a-data-source`). Skills never edit themselves, so don't change this file.
5. **Check for loose ends.** No stray pages, empty blocks or duplicate-named items. If something is unclear, such as where in the flow a new database belongs, choose sensibly, then tell the user what you chose and why.

Then, in the reply, say what you did to the layout, not just the thing that was asked for.

## Housekeeping

- The write tools can create databases (`create-database`) and change them (`update-a-data-source`), but they can only create views (`create-view`), never list or change them. So add a view only when you create its database. Normal filing never needs any of this. If a structural change is truly needed, **ask the user first**, and if the tools can't do it, tell them and stop.
- Existing views: To explore has "To review" (New only, oldest first) and "By status" (a board). Projects has "By stage" (a board grouped by Stage). Library has "Discussions" and "Videos & talks". Topics has "Recently updated". Learnings has "Learnings" (Kind = Learning) and "Insights" (Kind = Insight), plus the default view with both.
