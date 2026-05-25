# Thesis Submission

This directory contains the final Masters thesis for the VioNER
project, prepared for submission to the Department of Computer
Science, College of Natural Sciences, Addis Ababa University.

- `thesis.md` — authoritative source (markdown).
- `thesis.docx` — generated Word version. Build with `build_thesis.py`.
- `build_thesis.py` — build script (generates `reference.docx` and `thesis.docx`).
- `reference.docx` — pandoc reference template; regenerated on each build.

## Regenerating the Word version

```bash
cd backend/docs/thesis
# from inside the backend venv so python-docx is on PATH:
python build_thesis.py
```

The script does the following on a temp copy (source `thesis.md` is
never mutated):

1. Builds `reference.docx` programmatically with the AAU CS formatting:
   A4 paper, 1.3" left / 1" other margins, Times New Roman 12 pt, 1.5
   line spacing, justified body paragraphs, and Heading 1-4 styles.
2. Moves the Table of Contents block so it sits immediately after the
   cover/signature page and before the Abstract. The static TOC table
   is dropped; the heading is kept as the anchor for the real TOC.
3. Runs pandoc with `--reference-doc=reference.docx`.
4. Inserts a real Word TOC field (`TOC \o "1-3" \h \z \u \b "TOC_RANGE"`)
   at that heading, scoped to a bookmark covering Abstract → end of
   body so the title page and the TOC heading itself are excluded
   from the entries. Sets `<w:updateFields w:val="true"/>` so Word
   repaginates the TOC silently on first open; every entry hyperlinks
   to its heading.
5. Applies a 0.5 pt single-line black border to every table (pandoc
   emits borderless tables by default, which is not acceptable under
   AAU CS formatting).
6. Clears any direct paragraph-alignment overrides on body paragraphs
   so the justified Normal style wins uniformly.

The List of Tables, List of Figures, and List of Algorithms remain
manual tables in `thesis.md`; update them whenever a numbered figure,
table, or algorithm is added or removed.

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
