# Exegete

**Hallucination-resistant Bible exegesis for Claude — in Greek, Hebrew, English, and Korean.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/Bible%20data-CC%20BY%204.0-green.svg)](docs/DATA_SOURCES.md)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Give Claude a verse, and Exegete produces a rigorous **4-stage exegesis** — structure → original-language philology → theology & intertextuality → sermon framework. Unlike most AI Bible tools, **it never invents the text or the morphology**: every verse is pulled from real data, and every Greek/Hebrew parse comes from a tagged dataset, not the model's memory.

---

## Why Exegete is different

🛡️ **No hallucination of Scripture** — the biblical text is extracted by `lookup.py`, never recalled from memory. Original-language parsing comes from STEPBible's tagged data. Uncertain inferences are explicitly marked `[verify]`.

🔬 **Real original languages** — every Greek/Hebrew word with translation, Strong's number, morphology, and lemma.

🌏 **Multilingual** — input and read in **English or Korean**. Ships with the public-domain World English Bible; add your own translation (개역개정, etc.).

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

$ python src/word_search.py G26          # every occurrence of ἀγάπη (love)
총 114회 출현 — 요한일서(18), 고린도전서(14), 로마서(9) ...

$ python src/liturgical.py "Easter"      # lectionary readings
$ python src/series.py "Philippians"     # expository sermon series outline
$ python src/background.py "Exodus"       # historical background (with controversy flags)
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

**Use another translation** (e.g. Korean 개역개정 — supply your own, respecting its copyright):
```bash
# put data/<your-version>.txt  (one verse per line: "Gen1:1 In the beginning...")
EXEGETE_BIBLE=data/bible_krv.txt python src/lookup.py "요3:16"
```

---

## Modes

| Mode | Command / trigger | What it does |
|------|-------------------|--------------|
| **4-stage exegesis** | "Exegete \<ref\>" | structure → philology → theology → sermon |
| **Word study** | `word_search.py G26` | every occurrence of a Greek/Hebrew word |
| **Lectionary** | `liturgical.py "Easter"` | 13 church seasons, key readings |
| **Sermon series** | `series.py "Philippians"` | book split into preachable units |
| **Historical background** | `background.py "Exodus"` | people/events/journeys with controversy flags |
| **Devotional / study guide / reading plan / parallels** | see `CLAUDE.md` | lighter formats |

---

## Data & licensing

- **Code, prompts, methodology**: MIT.
- **World English Bible** (bundled): Public Domain.
- **Original languages** (via `setup_data.py`): STEPBible TAGNT/TAHOT, **CC BY 4.0** © Tyndale House, doctrinally neutral.
- **Copyrighted translations** (개역개정, NA28, BHS, Louw-Nida): **never bundled** — supply your own. See [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

## Korean support 🇰🇷

Exegete is built with first-class Korean support — input `요3:16`, Korean book names, and full integration with the 개역개정 (Korean Revised Version, user-supplied). Methodology and prompts are bilingual. 한국 교회·신학생을 위한 정확한 원어·주해 도구.

## Credits

4-stage structure inspired by and rewritten from [bible_analyze](https://github.com/mitmirsein/bible_analyze). Standard exegetical methods (pericope, discourse analysis, canonical trajectory, homiletics) are shared scholarly heritage. Original-language data by [STEPBible](https://github.com/STEPBible/STEPBible-Data) / Tyndale House.

## License

MIT (code) — see [LICENSE](LICENSE) and [NOTICE](NOTICE).
