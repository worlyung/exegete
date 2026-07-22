# Exegete

**🌐 English | [한국어](README.ko.md)**

**Hallucination-resistant Bible exegesis for Claude, Codex, and other agents — in Greek, Hebrew, English, and Korean.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/Bible%20data-CC%20BY%204.0-green.svg)](docs/DATA_SOURCES.md)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Give Claude a verse, and Exegete produces a rigorous **4-stage exegesis** — structure → original-language philology → theology & intertextuality → sermon framework. Unlike most AI Bible tools, **it never invents the text or the morphology**: every verse is pulled from real data, every Greek/Hebrew parse comes from a tagged dataset, and now **even the lexicon definitions are pulled from real dictionaries** — not the model's memory.

---

## What changed in this update

This update adds quality, safety, and publication guardrails around the existing Bible tools. It does **not** add an account system, a counselling-record database, or external transmission of requests.

| Area | What changed | What it means in practice |
|------|--------------|----------------------------|
| **Research discipline** 🆕 | Adopted humanities-research safeguards (inspired by [humanities-superpowers](https://github.com/icerain-cmd/humanities-superpowers)): observation vs. interpretation are kept distinct, every key interpretive claim must carry **at least one rival reading**, the same original-language word keeps the same translation throughout, and direct quotes attributed to theologians fall under the citation audit. | An exegesis can no longer present inference as observation, silently ignore competing readings, drift between renderings of one Greek/Hebrew word, or invent a Calvin quote — unverifiable attributions become `[verification needed]`. |
| **Concept lineage mode** 🆕 | "History of the doctrine of justification" style requests get their own mode: scripture usage first (`word_search`/`search`), then patristic → medieval → Reformation → modern lineage, with anachronism explicitly banned and contested points presented from both sides. | Doctrine-history answers start from actual biblical occurrences instead of memory, read each thinker by the questions of *their* era, and follow the same audit rules as everything else. Router + golden-set case `R16` included. |
| **Topic/source → sermon** 🆕 | Start from a **topic, article, or paper** (not a verse): `search` surfaces candidate texts, the pastor picks one, then 4-stage exegesis → sermon manuscript. | Candidate texts are never invented — only pulled from real search output — and the text is never reduced to a proof-text for the source material (eisegesis blocked). The pastor makes the final text choice. |
| **Sermon illustration audit strength** 🆕 | The factual audit of sermon illustrations & humanities citations is **dialed by interview**: `pulpit / standard / publication`. | Text, original language, and cross-references (hallucination-critical) stay strict always; only illustrations flex to pulpit language. Theological/applicational correctness is never judged. |
| **Multi-agent support** 🆕 | Added `AGENTS.md` so **Codex and other agents** — not just Claude — run under the same guidance, audit, and safety rules. | Tools are plain Python (agent-agnostic); methodology stays in `CLAUDE.md` as the single source of truth. |
| **Exegesis quality** | Added a required Genre Verdict, a Claim Ledger audit harness, and routing regression cases. | A 4-stage exegesis now separates literary genre, data-verifiable claims, and theological application before it is called complete. |
| **Context and series safety** | `lookup.py --pericope` falls back to the requested chapter with a warning when headings cannot establish a pericope; `series.py` refuses headingless data. | The tool no longer silently expands a request to an entire book or invents sermon-series units. |
| **Korean request router** | Added `python src/router.py "<request>"`. It returns a JSON plan with `direct_output: false` and never runs tools, creates content, saves, or echoes the request. | Korean requests can be classified consistently before a worker runs the existing Bible tools. High-controversy background topics are marked for review. |
| **Care and privacy boundary** | The router gives priority to immediate crisis or actual identifier patterns, while ordinary exegesis stays free of automatic safety text. | It asks for safe next steps rather than diagnosing, and it does not retain the request. See [`docs/CARE_SAFETY.md`](docs/CARE_SAFETY.md). |
| **Audited Word export** | Added `exegesis_state.py` and `export_exegesis_docx.py`. They bind a draft SHA-256, four completed stages, audit result, and WARN-consent file before export. | Changed drafts, `FAIL`/`HOLD`, incomplete stages, or unconsented `WARN` results cannot be exported through the audited path. `--all` preflights every draft before converting any; overwriting requires `--overwrite`. |

The older `src/export_docx.py` remains available as a general Markdown converter. It is not the audited-completion path for an exegesis.

---

## Why Exegete is different

🛡️ **No hallucination of Scripture** — the biblical text is extracted by `lookup.py`, never recalled from memory. Original-language parsing comes from STEPBible's tagged data. Uncertain inferences are explicitly marked `[verify]`.

🔬 **Real original languages** — every Greek/Hebrew word with translation, Strong's number, morphology, and lemma.

📖 **Real lexicon definitions** *(new)* — add `--lex` and each word gets its **full dictionary entry** (Greek: Abbott-Smith · Hebrew: BDB), pulled from data and matched by **exact extended Strong's number** so homographs never collide (בָּרָא "create" `H1254A` ≠ "be fat" `H1254B`). No more AI inventing *"according to BDAG…"* — entries that are missing or ambiguous are flagged `[verify]` instead of guessed.

🌏 **Multilingual** — input and read in **English or Korean**. Ships with the public-domain **World English Bible + 개역한글 (Korean Revised Version)**, so Korean works out of the box.

⛪ **Tradition-aware, bias-honest** — set your theological tradition; on debated historical questions (Exodus dating, etc.) it presents **both conservative and critical views** rather than asserting one.

---

## Demo

```bash
$ python src/lookup.py "John 3:16"
▶ John 3:16  For God so loved the world, that he gave his one and only Son,
             that whoever believes in him should not perish, but have eternal life.

$ python src/greek_lookup.py "John 3:16"
  ἠγάπησεν (ēgapēsen)  loved   [G0025 V-AAI-3S]  ← ἀγαπάω = to love
  μονογενῆ (monogenē)  only    [G3439 A-ASM]     ← μονογενής = unique
  πιστεύων (pisteuōn)  believing [G4100 V-PAP-NSM] ← πιστεύω = to trust

$ python src/greek_lookup.py "John 3:16" --lex    # + full lexicon definitions
  ἠγάπησεν (ēgapēsen)  loved   [G0025 V-AAI-3S]  ← ἀγαπάω = to love
      ▸ ἀγαπάω (agapaō) G0025 — to love
        to love, to feel and exhibit esteem and goodwill to a person...
        SYN.: φιλέω — love based on esteem (diligo), vs. spontaneous affection (amo)

$ python src/word_search.py G26          # every occurrence of ἀγάπη (love)
총 114회 출현 — 요한일서(18), 고린도전서(14), 로마서(9) ...

$ python src/liturgical.py "Easter"      # lectionary readings
$ python src/series.py "Philippians"     # expository sermon series outline (requires headed Bible data)
$ python src/background.py "Exodus"       # historical background (with controversy flags)
$ python src/router.py "John 3:16을 주해해줘"  # JSON plan only; does not run tools
```

Then in Claude Code, just ask: **"Exegete John 3:16"** — and `CLAUDE.md` drives the full 4-stage analysis.

---

## Quick start

```bash
git clone https://github.com/worlyung/exegete.git
cd exegete
python src/lookup.py "John 3:16"     # works immediately (World English Bible included)
```

**Add original languages** (Greek/Hebrew morphology, ~100 MB, CC BY):
```bash
python setup_data.py
```

**Add lexicon definitions** (Greek Abbott-Smith / Hebrew BDB, CC BY) — enables `--lex`:
```bash
python src/build_lexicon.py
```

**Korean works out of the box** — 개역한글 (Korean Revised Version, public domain) is bundled and auto-selected, no setup needed.

**Want 개역개정 (copyrighted)?** Supply your own copy — accessed legally via a Bible app or the Korean Bible Society — as `src/data/bible_krv.txt`, and it takes priority over 개역한글. Never redistribute it.

---

## Modes

| Mode | Command / trigger | What it does |
|------|-------------------|--------------|
| **4-stage exegesis** | "Exegete \<ref\>" | structure → philology → theology → sermon |
| **Word study** | `word_search.py G26` | every occurrence of a Greek/Hebrew word |
| **Lexicon definitions** | `greek_lookup.py <ref> --lex` | full dictionary entry per word (Abbott-Smith / BDB) |
| **Lectionary** | `liturgical.py "Easter"` | 13 church seasons, key readings |
| **Topic/source → sermon** 🆕 | "make a sermon on \<topic\>" / paste an article | topic → candidate texts → pastor picks → exegesis → manuscript |
| **Sermon series** | `series.py "Philippians"` | book split by explicit headings; headed Bible data required |
| **Historical background** | `background.py "Exodus"` | people/events/journeys with controversy flags |
| **Concept lineage** 🆕 | "history of \<doctrine\>" | scripture usage → patristic → Reformation → modern; anachronism banned |
| **Devotional / study guide / reading plan / parallels** | see `CLAUDE.md` | lighter formats |
| **Korean request plan** | `router.py "…"` | local JSON execution plan; never generates content or runs tools |

---

## Export to Word (.docx) 🖨️

Turn any exegesis (`output/*.md`) into a **formatted Word document** — headings, tables, original-language text, structure diagrams, and blockquotes are all preserved. Opens in **MS Word and Hangul (한컴 한글)** for editing, printing, and sharing.

An audited exegesis must first be registered, have all four stages complete, and have a
same-hash `PASS` audit (or an all-factual-claims-pass `WARN` with the exact consent file).
Then use the gated wrapper; it refuses unapproved or stale drafts and refuses overwrite
unless explicitly requested.

Or run it yourself — once `pip install python-docx`:
```bash
python src/export_exegesis_docx.py "output/Eph2_8-9.md"   # one audited draft
python src/export_exegesis_docx.py --all --overwrite        # all pass preflight before any conversion
```

The legacy `src/export_docx.py` remains compatible for non-gated manual conversion; do
not use it to declare an exegesis audit complete. See `harness/exegesis_audit.md` and
`docs/CARE_SAFETY.md` for the audit and care boundaries.

---

## Data & licensing

- **Code, prompts, methodology**: MIT.
- **World English Bible** (bundled): Public Domain.
- **개역한글 / Korean Revised Version (1961)** (bundled): © Korean Bible Society; copyright expired (2012) → free use, text kept unaltered with attribution.
- **Original languages** (via `setup_data.py`): STEPBible TAGNT/TAHOT, **CC BY 4.0** © Tyndale House, doctrinally neutral.
- **Lexicon definitions** (via `src/build_lexicon.py`): STEPBible TBESG (Abbott-Smith) / TBESH (BDB), **CC BY 4.0** © Tyndale House.
- **Copyrighted translations** (개역개정, NA28, BHS, Louw-Nida): **never bundled** — supply your own. See [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

## Korean support 🇰🇷

Exegete is built with first-class Korean support — input `요3:16`, Korean book names, and full integration with the 개역개정 (Korean Revised Version, user-supplied). Methodology and prompts are bilingual. 한국 교회·신학생을 위한 정확한 원어·주해 도구.

## Credits

4-stage structure inspired by and rewritten from [bible_analyze](https://github.com/mitmirsein/bible_analyze). Standard exegetical methods (pericope, discourse analysis, canonical trajectory, homiletics) are shared scholarly heritage. Original-language data by [STEPBible](https://github.com/STEPBible/STEPBible-Data) / Tyndale House.

## License

MIT (code) — see [LICENSE](LICENSE) and [NOTICE](NOTICE).
