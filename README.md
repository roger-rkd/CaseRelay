# CaseRelay

Confidence-gated triage for legal client enquiries, built on the Microsoft Power Platform (Dataverse, Power Automate, custom connector) with an LLM classifier on Groq.

Status: classification flow, evaluation harness, canvas intake and review queue, two security roles and the solution export are built and tested. The Reviewer role was tested with a second user. The Admin role is built but was not tested with a second user. The Copilot Studio agent was not built; see Limitations.

## Problem

A law firm receives free-text enquiries. An LLM can sort them into practice areas, but a model that is wrong and confident is worse than no model. The first version of this flow trusted the model's own confidence score. It failed: 29 of 37 answers scored exactly 0.95, and all six wrong answers scored 0.95 or higher. A confidence threshold alone did not separate right from wrong.

CaseRelay is about deciding when the system should not decide.

## Architecture

See [docs/architecture.md](docs/architecture.md).

- Dataverse: Case, Classification Run (every classification logged with raw signals), Evaluation Item.
- Power Automate: `CaseRelay Classify` (live) and `CaseRelay Evaluate` (runs the labelled set through the same prompt and gate).
- Custom connector: `connector/groq-classifier.yaml`, API key authentication (not OAuth).
- Canvas app `CaseRelay Review Queue`: an intake screen that creates a case, and a review queue for escalated cases (claim, resolve with notes). Readable source is in `solution/canvas-src/`.
- Security roles: `CaseRelay Reviewer` and `CaseRelay Admin`.
- Environment variables: classifier model, confidence threshold, minimum word count.
- Connection references: Dataverse and Groq, so the solution imports without credentials.

## How gating stays safe

A case is auto-resolved only if every check passes. Any single failure escalates to a human with a recorded reason.

1. Rule check: fewer than 8 words, or an instruction-override phrase, escalates before the model result is used.
2. The model must say the text is a legal matter.
3. The model must not flag it ambiguous.
4. The model must say the context is sufficient.
5. Confidence must meet the threshold (0.7).
6. The alternative category must be "None" or "Other". A real competing category escalates.
7. Any model or connector error escalates (Try/Catch scope), reason Model Error.

The enquiry is wrapped in tags and the system prompt treats it as data. Prompt injection is also caught by rule, so the model is not the only defence.

Every run stores the raw model signals, so a different gate can be replayed offline without new model calls. The gate in step 1 to 7 was committed before Holdout 2 was run.

## Evaluation

Model `openai/gpt-oss-20b`, JSON mode, temperature 0, reasoning effort low. Full tables, method and limitations: [evaluation/RESULTS.md](evaluation/RESULTS.md). Numbers are recomputed from `evaluation/runs_export.csv` by `evaluation/analyse.py`.

Dev set (37 items, 23 should escalate, 14 clear):

| | v1 | v3 + committed gate |
|---|---|---|
| Category accuracy | 83.8% | 94.6% |
| Wrong category auto-resolved | 6 | 0 |
| Should-escalate caught (of 23) | 1 | 21 |
| Clear cases wrongly escalated (of 14) | 0 | 4 |

Fresh holdout (12 items, v3 + committed gate): 12 of 12 correct category, 7 of 8 should-escalate caught, 0 of 4 clear cases wrongly escalated, no silent wrong answer.

The trade is deliberate: more escalations in exchange for no silent errors on these sets.

## Security

The Groq key is entered in the connection only. The exported solution was scanned and contains no key; environment variables hold non-secret settings only (Secret-type variables need Azure Key Vault and are not used).

Roles:

- `CaseRelay Reviewer`: read and update Cases, create Cases (intake), claim and resolve. No access to Evaluation Item and no delete on Cases.
- `CaseRelay Admin`: built, not tested with a second user.

The Reviewer role was tested with a second user (CaseRelay Tester) in a private browser session. Results, with screenshots in [docs/evidence](docs/evidence/README.md): can read cases, can claim and resolve, can submit an enquiry; cannot read Evaluation Item; cannot delete a case.

Finding from that test: the first Claim attempt failed with `prvAppendToUser` missing on the User table, because Assigned Reviewer is a lookup to User. The role needed User Read and Append To (Organization). A first fix that set Append instead of Append To did not work. Both are in the evidence folder.

The canvas app reports save results from `Errors(Cases)`. An earlier version used `IfError`, which showed a success banner next to a real error.

## Limitations

- Small sets (37 and 12 items), written by the author. Holdout percentages are indicative only.
- One model, one provider.
- The ambiguity and legal-matter flags are self-reported by the model. The gate escalates 4 of 14 clear dev cases, and these sets over-represent hard cases, so the escalation rate is not a production figure.
- Holdout 2 miss: H2-007 (neighbour's tree and an insurer liability dispute) gave no uncertainty signal.
- Dev results for the gate are tuned. Holdout 1 informed v3 and is no longer clean.
- Built in a personal developer tenant with no real users.
- No Copilot Studio agent. Creating an agent returned "User license not found" in this personal tenant, and a tenant capacity trial did not clear it. The canvas intake screen and the flow take its place; nothing here claims an agent.
- Admin role not tested with a second user.
- Live runs CR-00010 to CR-00016 predate the v3 flow update and are labelled v1; CR-00017 onward use the committed v3 gate. The Classification Run table keeps both.
- Evaluation runs are started by the owner from Power Automate, not from the canvas app.
- Connector authentication is an API key.

## Repo layout

```
connector/    Groq custom connector definition
evaluation/   labelled sets, raw run export, analysis script, results
prompts/      v1, v2, v3 system prompts
solution/     exported unmanaged solution 1.0.0.3 (zip and unpacked), canvas-src/ readable canvas formulas
docs/         architecture, evidence/ (security and app test screenshots)
```

## Reproduce

Import the solution, create the Groq connection with your own key, set the three environment variables, run `CaseRelay Evaluate` after importing the CSV sets into Evaluation Item.

## Known inconsistency

`CaseRelay Evaluate` uses a run-as-invoker Groq connection reference, while `CaseRelay Classify` uses an embedded connection. Evaluate is only run manually by the owner, so behaviour is unaffected.
