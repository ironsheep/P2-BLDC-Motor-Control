# Spin2 style — the T2 audit

The Spin2 authoring guide (`central:spin2-authoring-guide`) assigns every rule a tier. `tools/check_style.sh`
enforces the T1 rules and prints, on every run, what it does not check. This document is the home of what it
does not check: the **T2** rules, which need a reader's judgement, and the **judge half** of the five T1+T2
rules, whose detection a script could do but whose verdict needs a reader. The two **T3** rules are Stephen's
read, not an audit.

## The rules this audit owns

| Guide | Rule | What the reader decides |
| --- | --- | --- |
| 1.7 | Pointer semantics differ from C | `@@` on a DAT-stored address; `[ptr]` on a struct-pointer return |
| 2.1.1 | Vowel-removal shortening | the shortened name can be sounded out |
| 2.1.2 | Globals spelled out, locals shortened | VAR/DAT names are full words |
| 2.1.3 | Consistent base names across methods | one concept, one base name |
| 2.2 | No generic container names | the name says what data it carries (beyond the seven the gate enumerates) |
| 2.3 | Return variables named for their data | the return name describes the result |
| 3.3 | Conditional-compilation discipline | every `#ifdef` block is self-contained; no ungated method inside one |
| 3.5 | CON block organisation | related constants grouped, no fragmented blocks |
| 3.6 | DAT vs VAR semantics | singleton state in DAT, per-instance state in VAR |
| 4.3 | PUB documentation (the prose) | the description is current and says what the method does |
| 4.4 | PRI documentation (the prose) | as 4.3 |
| 4.7 | Enumerated constant groups | a preceding comment lists every value |
| 4.8 | STRUCT declarations | a preceding comment lists every member |
| 4.10 | Internal block comments | multi-line internals use `{ }`, never `{{ }}` |
| 5.4.2 | Named constants communicate intent | the name says why the value matters |
| 5.5 | Multiple returns over pointer out-parameters | an out-parameter is justified (buffer, shared memory, PASM) |
| 5.6 | Never overwrite a specific error | a caller keeps the callee's error code |
| 6.3, 6.5, 6.6 | Regression-test rules | not applicable: this project has no Spin2 regression harness (Part 6 is conditional) |
| 2.1.4 (judge) | Numbered suffixes | numbered only when the items are interchangeable |
| 2.5 (judge) | Same name, same description | one `@param` description per parameter name, across methods |
| 4.6 (judge) | CON/VAR/DAT declaration comments | important descriptions precede; brief annotations trail |
| 5.7 (judge) | No magic numbers | every semantic literal is a named constant (0, -1 and 4 excepted) |
| 6.1 (judge) | Test comparisons use named constants | not applicable, as Part 6 above |

T3, Stephen's: **5.8** (dedicated-cog architecture) and **5.9** (shared-bus switching).

## When it runs, and on what

- **Diff-scoped, at every task that changes `.spin2` source:** the files and methods the task's diff touched,
  before the task closes.
- **Rotating sweep, one per sprint:** the authored files in turn, oldest audit first, so every file is read
  against every T2 rule within a bounded number of sprints.
- The surface is the style gate's own: every `src/*.spin2` except the imported files the gate names.

## How a finding is written

A finding without a `file:line` is not a finding. Each one names the rule, the site, what is wrong, and the
correction; a correction that changes a public name or signature is a compatibility question for Stephen, not
an edit.

## The audit record

Every audit writes one record to `DOCs/analyses/style-audits/`, named `T2-AUDIT-<yyyy-mm-dd>-<commit>.md`:

- **Commit audited** — the full hash of the tree that was read. An audit is valid for that commit only.
- **Scope** — diff-scoped (the task and its diff) or sweep (the files).
- **Rules** — which of the rules above were applied.
- **Files** — every file read.
- **Findings** — `file:line`, rule, what is wrong, disposition (fixed in which commit, or punch-listed as PL-N).
- **Clean** — the rules applied that found nothing, stated, so an empty findings list is a result and not a gap.

## The limit, stated

An agent can write a record in this format without doing the reading it describes, and nothing in the record
proves otherwise. The record makes an audit **checkable** — its findings can be re-read at the named commit —
not **self-proving**. What gives it weight is that its clean rules can be spot-checked: pick a rule the record
calls clean, read one of its files, and see.
