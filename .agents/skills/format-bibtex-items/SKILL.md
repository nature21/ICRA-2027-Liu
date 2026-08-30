---
name: format-bibtex-items
description: Format, add, or clean BibTeX entries in this paper's references.bib file. Use when a user selects or supplies a BibTeX item, asks to normalize bibliography formatting, remove redundant citation fields, or make an entry comply with the project's bibliography style without comparing it with neighboring entries.
---

# Format BibTeX Items

Apply the rules below directly. Do not scan other bibliography entries merely to rediscover the style.

## Workflow

1. Identify the entry type and whether an `@article` is an arXiv preprint or a published journal article.
2. Preserve the citation key, bibliographic facts, author order, name spelling, and TeX escapes unless the user requests a content correction.
3. Apply the appropriate field schema and remove fields classified as redundant below.
4. Edit only the selected or requested entry. Do not reformat unrelated entries.
5. Check balanced braces, commas, page ranges, and the closing delimiter after editing.

## Layout

- Indent fields by two spaces.
- Put one space on each side of `=`.
- Wrap values in braces.
- Wrap titles in double braces to preserve capitalization: `title = {{...}}`.
- Normalize titles to title case. Preserve official acronym and product-name
  stylization, such as `SAM`, `3D`, `6D`, `FoundationPose`, and `MuJoCo`.
- Put one field on each line in the order defined below.
- End every field except the last one with a comma.
- Leave one blank line between entries.
- Write page ranges with a double hyphen, such as `19--67`.
- Format authors as `Family, Given and Family, Given`. Preserve `and others` when supplied.
- Preserve an existing citation key. For a new key, use lowercase `{lead-author}{year}{first-title-word}`, omitting spaces and punctuation.

## Field schemas

Use this exact arXiv article form:

```bibtex
@article{key,
  title = {{Title}},
  author = {Family, Given and Family, Given},
  journal = {arXiv:YYMM.NNNNN},
  year = {YYYY}
}
```

Use this order for a published journal article:

```bibtex
@article{key,
  title = {{Title}},
  author = {Family, Given and Family, Given},
  journal = {Journal Name},
  volume = {N},
  number = {N},
  pages = {N--N},
  year = {YYYY}
}
```

Keep `volume`, `number`, and `pages` only when they are supplied and applicable; do not invent missing data.

Use this conference-paper form:

```bibtex
@inproceedings{key,
  title = {{Title}},
  author = {Family, Given and Family, Given},
  booktitle = {Venue Abbreviation},
  year = {YYYY}
}
```

Use the standard conference abbreviation alone in `booktitle` when one is
well established, such as `CVPR`, `ICLR`, or `IROS`. Omit the year, publisher
prefix, and expanded proceedings title.

For `@book`, use `title`, `author`, `year`, then `publisher`. For `@misc`, use `title`, `author`, `note`, then `year`, omitting fields that do not apply. For any other entry type, apply the layout rules while preserving necessary type-specific fields.

## Redundant fields

- Remove `doi`, `url`, `month`, `issn`, `isbn`, `abstract`, and `keywords` from articles and conference papers.
- For arXiv articles, replace `eprint`, `archivePrefix`, and `primaryClass` with the compact `journal = {arXiv:<identifier>}` field.
- Do not remove `volume`, `number`, or `pages` from a published journal article merely to shorten it.
- Keep `publisher` for books and keep a URL in `note` for software or project citations represented as `@misc`.
- Do not add fields that are absent from the supplied citation unless the user explicitly asks to complete its metadata.
