# Evidence

Screenshots from testing CaseRelay with a second user (CaseRelay Tester, Reviewer role). Browser chrome is cropped out. Nothing here shows a key or secret.

| File | What it shows |
|---|---|
| 01-reviewer-reads-cases.png | Reviewer can read Cases through the Dataverse web API. |
| 02-reviewer-claim-blocked-missing-append-to.png | First Claim attempt as Reviewer failed: missing prvAppendToUser on User. Fixed by adding User Read and Append To (Organization) to the role. |
| 03-reviewer-claim-success.png | Claim succeeds after the fix, with only the success banner. |
| 04-reviewer-claim-recorded-in-cases.png | The claimed case is In Review, Assigned Reviewer is CaseRelay Tester, Claimed On is set. |
| 05-reviewer-denied-evaluation-item.png | Reviewer cannot read Evaluation Item (prvReadcr_EvaluationItem missing). |
| 06-reviewer-denied-delete-case.png | Reviewer cannot delete a case (prvDeletecr_Case missing). The green "Deleted" banner beside the red error comes from the earlier IfError pattern in a temporary test button, which reports success even when the write fails. The real outcome is the red error. The app now checks Errors(Cases) instead, and the test button has been removed. |
| 07-reviewer-resolve-recorded-in-cases.png | Reviewer resolves a case. CR-00012 shows status Resolved, the resolution note, Resolved On and Claimed On, with CaseRelay Tester as reviewer. CR-00016 is test data from before the Claim fix. |
| 08-live-run-threshold-0-7.png | Live classification runs log Threshold Applied 0.70. Runs CR-00010 to CR-00016 predate the v3 flow update and are labelled v1; CR-00017 onward use the committed v3 gate. |
| 09-intake-submitted-cr-00017.png | Intake form submits an enquiry and returns a case reference (shown in Power Apps Studio preview). |
| 10-classify-flow-run-succeeded.png | The Classify flow run for that case succeeded. |
| 11-intake-submitted-by-reviewer-cr-00018.png | The Reviewer user can also submit an enquiry. |

Not tested with a second user: the Admin role.
