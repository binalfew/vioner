# Thesis Submission

This directory contains the final Masters thesis for the VioNER
project, prepared for submission to the Department of Computer
Science, College of Natural Sciences, Addis Ababa University.

- `thesis.md` — authoritative source (markdown).
- `thesis.docx` — generated Word version (`pandoc thesis.md -o thesis.docx --toc --toc-depth=3`).

## Regenerating the Word version

```bash
cd backend/docs/thesis
pandoc thesis.md -o thesis.docx --toc --toc-depth=3
# Alternative with a reference template for AAU formatting:
pandoc thesis.md \
  --reference-doc=aau-thesis-template.docx \
  --toc --toc-depth=3 \
  -o thesis.docx
```

**Important:** the `--toc --toc-depth=3` flags are required. The
Table of Contents is **not** written manually in `thesis.md` (per the
AAU guideline, "Table of contents must be generated automatically and
not manually"); pandoc generates it from the chapter and section
headings at build time. The List of Tables, List of Figures, and List
of Algorithms are kept as manual tables in `thesis.md` because pandoc
does not auto-generate them — update them whenever you add or remove
a numbered figure, table, or algorithm.

## Formatting requirements (from AAU CS guideline)

Apply these in Word after conversion:

- A4 paper, 12-point Times New Roman.
- 1.5 line spacing throughout.
- Margins: 1.3 inch left, 1 inch top / right / bottom.
- Title page, signature page, abstract, dedication, and acknowledgements
  have no page numbers.
- Table of Contents through Acronyms: lower-case Roman numerals
  (i, ii, iii, …), bottom-centre.
- Chapter 1 onwards: Arabic numerals (1, 2, 3, …), bottom-centre.
- IEEE citation style (already used in `thesis.md`).
- The final page is the signed Declaration Sheet.

## Items to verify before submission

1. Re-run the evaluation script and update Tables 6.3, 6.4, 6.5 with
   the latest numbers from your chosen production model:
   ```
   python backend/services/evaluation.py \
     --model models/active \
     --val data/processed/val.jsonl \
     --report
   ```
2. Replace screenshot placeholders in Annex D with actual screenshots
   from the deployed web application.
3. Confirm references [11] (MasakhaNER) and any other added citations
   are correctly listed by IEEE rules.
4. Add advisor name, examiner names, and the official defence date to
   the signature page.
5. Add the dedication line as desired (current draft is generic).
6. Run a spell/grammar pass; the markdown source uses Commonwealth
   spelling (organisation, optimised) — adjust if your committee
   prefers US English.

## Items NOT included on purpose

The following items from the AAU final-submission package (Annex D of
the guideline) are produced separately and not part of this markdown
source:

- Three bound copies (printed and signed).
- CD with soft copy (Word + PDF), abstract, user manual, source code,
  sample data, reference materials, and tools.

These should be produced after the defence and after any
post-defence revisions.
