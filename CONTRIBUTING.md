# Contributing to Exegete

Thanks for your interest! Exegete aims to be a **reliable, hallucination-resistant**
Bible study tool. Contributions are welcome.

## Ground rules
- **Never bundle copyrighted texts** (개역개정, NA28, BHS, Louw-Nida, etc.). Only
  public-domain or CC-licensed data (see `docs/DATA_SOURCES.md`).
- **Accuracy over fluency.** If the data doesn't support a claim, mark it `[verify]`.
- **Bias-honest.** On debated historical/theological questions, present multiple views.

## How to contribute
- 🐛 **Bug / wrong data**: open an issue with the exact verse and command.
- ✨ **New mode or translation support**: open an issue to discuss first.
- 🌍 **New language**: book-name mappings live in `src/data/book_abbrev.json`.

## Dev setup
```bash
git clone https://github.com/worlyung/exegete.git
cd exegete
python src/lookup.py "John 3:16"   # WEB bundled, works immediately
python setup_data.py               # optional: Greek/Hebrew data
```
No dependencies beyond Python 3.8+ standard library.
