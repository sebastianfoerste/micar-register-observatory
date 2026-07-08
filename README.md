# The State of the MiCAR Register

A quarterly data report on the EU's crypto-asset white paper register. It answers one question with numbers instead of anecdote: how much of the MiCAR register is actually the structured, machine-readable disclosure that Article 109 intends?

The current finding, from the latest snapshot: **of the crypto-asset white papers on the register, only about 12% are published in a structured machine-readable format, and around 61% link nothing but a landing page.**

Latest edition: **[editions/2026-Q3.md](editions/2026-Q3.md)** · shareable page: **<https://sebastianfoerste.github.io/state-of-the-micar-register/>**

## Why it exists

MiCAR's Article 109 requires ESMA to keep crypto-asset white papers in a machine-readable register so disclosures can be compared, queried, and checked across the single market. Nobody was measuring whether the register delivers that. This report does, on a quarterly clock, from public data.

## How it works

Every figure is generated from the [MiCAR Register Observatory](https://github.com/sebastianfoerste/micar-register-observatory), which snapshots the five public ESMA register CSVs weekly and commits the diff. Each edition is built from one dated snapshot, so its numbers are reproducible from a commit. The narrative in each edition is human-authored; the data tables between the `data:start` / `data:end` markers are generated.

```bash
git clone https://github.com/sebastianfoerste/state-of-the-micar-register
cd state-of-the-micar-register
make install && make test
make build            # regenerate the latest edition's data section + docs/index.html
```

## What this is and is not

This report states facts about a public register — counts, formats, Member States. It makes no assessment of any named issuer and asserts no white paper is unlawful or deficient. A landing-page link is a fact about a register entry, not a judgment about the disclosure behind it. Not legal advice.

## Editions

| Edition | Snapshot | Headline |
| --- | --- | --- |
| [2026-Q3](editions/2026-Q3.md) | 2026-07-07 | ~12% of white papers machine-readable; ~61% landing-page only |

Author: Sebastian Förste — German-qualified lawyer (EU financial regulation), former NLP data scientist. Code is MIT; the report text may be cited freely with attribution.
