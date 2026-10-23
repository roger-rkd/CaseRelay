# CaseRelay evaluation results

Model: `openai/gpt-oss-20b` on Groq, JSON mode, temperature 0, reasoning effort low. Same model and settings in every run. Only the prompt and the escalation gate changed.

Every run logs the raw model output, so any gate can be applied afterwards. All numbers below are computed from the exported Dataverse table, not read by hand.

## Sets

| Set | Items | Role |
|---|---|---|
| Dev | 37 (EV-001 to EV-037) | Used to design and tune v2 and v3 |
| Holdout 1 | 12 (HO-001 to HO-012) | Run on v2 once. Its failures informed v3, so it is no longer clean |
| Holdout 2 | 12 (H2-001 to H2-012) | Written before v3 results existed. Run once on v3 with the gate committed in advance |

Dev mix: 14 clear, 8 ambiguous, 8 thin, 7 adversarial. 23 of 37 items should escalate to a human.

## Dev set (37 items)

| | v1 | v2 | v3 (model flags only) | v3 + committed gate |
|---|---|---|---|---|
| Category accuracy | 31 (83.8%) | 37 (100%) | 35 (94.6%) | 35 (94.6%) |
| Escalation rate | 1 (3%) | 29 (78%) | 16 (43%) | 25 (68%) |
| Should-escalate caught (of 23) | 1 | 21 | 16 | 21 |
| Clear cases wrongly escalated (of 14) | 0 | 8 | 0 | 4 |
| Wrong category auto-resolved | 6 | 0 | 0 | 0 |

v1 is the original prompt with a 0.7 confidence gate. 29 of 37 answers scored exactly 0.95 and all six wrong answers scored 0.95 or higher, so confidence did not separate right from wrong.

## Fresh holdout (Holdout 2, 12 items, v3)

| | v3 (model flags only) | v3 + committed gate |
|---|---|---|
| Category accuracy | 12 of 12 | 12 of 12 |
| Escalation rate | 5 of 12 | 7 of 12 |
| Should-escalate caught (of 8) | 5 | 7 |
| Clear cases wrongly escalated (of 4) | 0 | 0 |
| Wrong category auto-resolved | 0 | 0 |

The one miss under the committed gate is H2-007 (a neighbour's tree and a liability dispute), where no signal indicated uncertainty.

v1 and v2 were not run on Holdout 2, so there is no head to head comparison on fresh data.

## Committed gate

Escalate if any of: a rule fires (fewer than 8 words, or an instruction-override phrase), the model says the text is not a legal matter, the model flags it ambiguous, the model says the context is insufficient, confidence is below 0.7, or the alternative category is a real competitor (anything other than "None" or "Other").

The gate was fixed before Holdout 2 was run. It was chosen after looking at v3 dev results, so the dev numbers for it are tuned and the Holdout 2 numbers are the fair test.

## Limitations

- Small sets (37 and 12 items), written by the project author. Percentages on 12 items are indicative only.
- One model, one provider. Results may not transfer.
- The ambiguity and legal-matter flags are self-reported by the model. v2 over-fired the ambiguity flag (8 of 14 clear cases escalated) and v3 under-fired it (1 of 8 ambiguous items). The alternative-category gate recovers most of the gap but still escalates 4 of 14 clear dev cases.
- Even the best gate escalates more than half of the traffic on these sets. These sets over-represent hard cases, so this is not a production escalation rate.
- v3 regressed on two dev items (EV-022, EV-027), which drifted back to Dispute. Both were escalated, so neither was a silent error.
- Prompt rules for "Other" (wills, probate and similar) and the legal-matter field were added after observing specific failures, so those fixes are tuned to observed errors.
