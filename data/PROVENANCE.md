# Data provenance

## combined_priority.csv

Snapshot of `outputs/combined_priority.csv` from the
[csf-sme-coverage](https://github.com/Viru1998/csf-sme-coverage) pipeline.

| Field | Value |
|---|---|
| Source commit | `f0e0beac178d1cbb62ec22eed2fadc2deebcbcd8` |
| Source path | `outputs/combined_priority.csv` |
| Copied | 2026-09-28 |

The file is copied byte-for-byte and must not be edited by hand. To refresh it
after the pipeline is re-run, copy the new file from a pinned commit and update
the table above:

```bash
git -C ../csf-sme-coverage show <commit>:outputs/combined_priority.csv > data/combined_priority.csv
```

The app reads only the `subcategory` and `combined_score` columns
(`combined_score` = Verizon DBIR threat weight × Irish adoption gap).
