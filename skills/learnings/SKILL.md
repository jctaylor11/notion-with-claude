---
name: learnings
description: Save what the user has understood, in their own words, to the Learnings database in their Notion workspace. Use when the user says "add this to my learnings", "save this learning" or "save this insight", points at something they just explained and wants it kept, or shares something from a source that struck them. Every write waits for their approval.
---

# Learnings

The Learnings database is a faithful record of the user's own understanding, so every row must read as if they wrote it. Use the `notion-write-test` tools for every write and the `notion-read-test` tools to read. If a tool is missing, or a write target is outside the workspace page, stop and tell the user. Never call the Notion API another way.

## State

At the start of every task, read `${CLAUDE_PLUGIN_DATA}/config.json`. If it's missing, stop and tell the user to run `/notion-workspace:setup`. Use its `learnings` data source for the rows, and its `library` data source to link the resource the user was going through. Never write IDs into this file. The user's edits to a learning's wording count as style feedback and go to `${CLAUDE_PLUGIN_DATA}/learned-style.md`, the same file the `notes` skill learns into.

## Database

**Learnings** (one row per discrete thing the user has understood, in their own words). If the user has a database called Learnings elsewhere in their Notion, that one is theirs and read-only for me; only ever write to the one in `config.json`:
- Name: a short noun phrase in the user's own terms, 2–4 words, like "MCP servers" or "Client vs conn".
- Kind: Learning (the user's own conclusion, which they worked out) or Insight (something from a source that struck them, e.g. a speaker's idea). Always set it.
- Library: relation to the Library row for the resource the user was going through, synced back as "Learnings". Set it whenever they say what they were watching or reading and it's already in the Library.
- Insight: the learning or insight, in the user's own words (see "Saving a learning").
- Context: one factual line on what prompted it, e.g. "While reading the notion-mcp-server codebase".
- Origin: Discussion with Claude, Reading, Building, Video or Other. Set from fact, never guessed.
- Tags: 1–3 short subject tags. Reuse a tag already in the database when it fits, and add a new one whenever none describes the learning well. Don't force the user's other databases' tags onto it.
- Topics, Projects: relations, only when one clearly fits. Both sync back automatically as "Learnings".
- Added: set automatically.
- Page body: the user's original message, verbatim, in a toggle (Learnings only; Insights have no body).

## Saving a learning

Trigger: the user says to add or save a learning, or points at something they just explained and wants it kept. The point of the database is a faithful record of the user's own understanding, so the row must read as if they wrote it.

**Approval first (applies to every write to Learnings, learnings and insights alike).** Before calling any write tool for the Learnings database, show the user the core insight text I propose to save, and nothing else (no title, tags or other properties). Wait for their approval. Do the duplicate check and all other preparation first, but make no create or update call until they say yes. If they edit the wording, show the revised text again only if the change was substantial. If the write tools are unavailable, still show the draft and say it can't be saved yet. Approval for one batch doesn't carry over to later ones.

1. **Take their words, from the message or messages they point to.** Not mine. If they restated something I said, use only their restatement.
2. **Tidy, never rewrite.** Allowed: reorder, trim conversational filler, questions addressed to me, and repetition; join into a few short paragraphs; fix typos; end on their own closing rule if they stated one. Keep their phrasing, analogies, examples and first-person voice. Not allowed: adding facts, my corrections or explanations, or terms they didn't use.
3. **If their version is imprecise or wrong, keep it as they said it** and tell them in chat what I think is off, so they decide whether to change it. Never silently fix it.
4. **Name** it with a short noun phrase in their terms. **Context** is one factual line. Set **Origin** and **Tags** yourself, and never ask the user to choose any metadata.
5. **Check for duplicates.** Query Learnings by Name. If something similar exists, say so and ask whether to add to it or make a new row.
6. **Create the row** with `post-page` (parent: the Learnings data source from `config.json`), Insight set, and a 💡 icon. Then write the page body with `update-page-markdown`: a toggle titled "Original message" containing the user's text verbatim.
7. **Link** to a Topic or Project only if one clearly fits. Don't create topics for a learning, and don't edit topic pages.
8. **Reply briefly:** the row link, and one line on what was trimmed or reordered. Include any imprecision from step 3.
9. If the user later edits the Insight, treat the change as direct style feedback and add it to `learned-style.md`.

**Teaching beyond their words.** When the user asks for the accurate, fuller explanation to be kept with a learning, put it in the page body *after* the "Original message" toggle, under the heading `## Going deeper (written by Claude, not in the author's words)`. The Insight property and the toggle stay purely theirs; only this section may contain my words. It should: say what was checked and when, separate what holds up from what needs correcting, and list anything still unconfirmed. Only include what I've verified in the source (e.g. the code), and mark the rest as unconfirmed. Don't add it unprompted. If the topic deserves a standing synthesis across sources, that belongs on the Topic page instead.

### Saving an insight

Trigger: the user shares something from a source that struck them ("X says that...", "I found it insightful that..."). It uses the same database and the same faithfulness rules as a learning, with these differences:
- **Kind** is Insight. Name is a short noun phrase. Insight is their own words, tidied, and can be one line or a short paragraph; keep the attribution they gave ("In Matt Pocock's talk, he says...").
- **Library link is the point.** Find the resource in Library (search by name or speaker). If it's there, link it and set Origin to match (Video, Reading...). If it isn't, don't create an empty Library row: say so and offer to add it to To explore.
- No toggle or page body. Skip Context unless there's something beyond the source itself.
- Duplicate check, tags and the short reply work as for a learning.
- If the user's own conclusion is in the message (a Learning, not just a captured idea), use Kind Learning; if a message has both, make two rows.
- Learnings should also get the Library link when the user names the resource they were going through.
