# How Machine-Checkable Is IAB Privacy Signaling?

Artifacts for the preprint *How Machine-Checkable Is IAB Privacy Signaling? Syntax versus Meaning on the Wire* (Sekowski, August 2026, v1.0). Paper 5 of the checkability series.

Preprint source: `preprint-privacy-signaling.md`  
PDF: `build/privacy-signaling-preprint.pdf`

Citable copy: https://github.com/aleksUIX/iab-privacy-checkability  
DOI: https://doi.org/10.13140/RG.2.2.24242.16320  
ResearchGate: https://www.researchgate.net/publication/413765958_How_Machine-Checkable_Is_IAB_Privacy_Signaling_Syntax_versus_Meaning_on_the_Wire  
OpenAdTech: https://openadtech.org/research/#iab-privacy-signaling

## Reproduce the numbers

Python 3, stdlib plus matplotlib for figures.

```bash
python3 extract.py         # data/statements.csv from specs/pinned/
python3 code.py            # author labels -> data/statements_coded.csv
python3 reliability.py     # delayed recode, n=40, seed 20260822
python3 finalize.py        # data/final_stats.json (needs paper 3 issues.csv for leftover GDPR)
python3 figures.py         # figures/
python3 check_numbers.py   # manuscript vs final_stats
```

`measure_wild.py` walks paper 3's private request bodies and writes site counts only. The released `data/wild_privacy.json` is frozen. You do not need the payloads to recompute Table 1, Table 2, Table 3, or the figures.

Every headline number in the paper is produced by one of those scripts. Changing a label in `code.py` moves Table 1 and Figure 2 on the next run.

PDF rebuild (pandoc + weasyprint):

```bash
bash build/build-pdf.sh
```

## Headline counts (scripted)

- 221 keyword sentences, 59 excluded (X), 162 conformance
- Full portfolio: S1+S2 35.8%; M0 54.3%; M1 37.7%; M2 8.0%; M3 0; green cell 24.7%
- Leave-one-out: drop TCF, S1+S2 50.7%; GPP string only, 61.5% S1+S2 and 76.9% M0
- Wire subset: n=121, S1+S2 47.1%
- Live traffic: 20,226 requests, 165 sites, six paper 3 captures
- Paper 3 leftover `regs.ext.gdpr`: 38 of 79 sites (frozen issues)
- Sample A wave 3: GPP 40/79, US National 21/79, TCF EU 0/79, `coppa=1` 0/79
- Those zeros hold on Sample B (90 sites) and on all six waves

## Layout

| path | what |
|---|---|
| `data/statements_coded.csv` | 221 keyword sentences, author labels plus heuristic seed |
| `data/reliability.json` | recode sample, disagreements, kappas |
| `data/wild_privacy.json` | site counts, no payload values |
| `data/final_stats.json` | every number quoted in the paper |
| `specs/pinned/` | GPP, TCF, US Privacy, OpenRTB privacy excerpts |
| `PINS.json` | GitHub SHAs and the OpenRTB SHA-256 |
| `CODEBOOK.md` | syntax/meaning classes |

Full spec clones under `specs/{gpp,tcf,usprivacy}` are gitignored. `finalize.py` reads paper 3's public `dataset_sampleA/issues.csv` for leftover `regs.ext.gdpr`. Request bodies stay private.

## License

Preprint text, PDF, and figures: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).  
Code and data: [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

## Cite

See `CITATION.cff`. doi:10.13140/RG.2.2.24242.16320

Paper 4 in this series: ResearchGate 413532379.
