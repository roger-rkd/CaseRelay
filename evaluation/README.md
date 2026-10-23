# Evaluation data

- `dev_set.csv`, `holdout1_set.csv`, `holdout2_set.csv`: labelled enquiries.
- `runs_export.csv`: raw Dataverse export of every evaluation run (prompt versions v1, v2, v3). Choice columns hold option values: 121590000 Commercial, 121590001 Employment, 121590002 Property, 121590003 Dispute, 121590004 Other. In `cr_runtype`, 121590001 is Evaluation.
- `analyse.py`: recomputes every number in `RESULTS.md` from `runs_export.csv`. Run with `python3 analyse.py runs_export.csv`.
- `RESULTS.md`: tables and limitations.
