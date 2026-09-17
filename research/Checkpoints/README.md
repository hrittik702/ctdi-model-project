# Daily Research Checkpoint System

This directory contains the immutable, chronological session logs for every working day on the **Air Pollution Missing-Data Imputation (SLM-Conditioned Diffusion)** project.

---

## 1. Checkpoint Philosophy & Rules

1. **One Checkpoint per Working Day**: Every meaningful research, engineering, or auditing session produces exactly one dated file:
   ```text
   research/checkpoints/YYYY-MM-DD.md
   ```
2. **Historical Immutability**: Historical checkpoints are immutable scientific records. Never rewrite, erase, or retroactively alter a past checkpoint.
   - If a past finding is later found to be incorrect, do **not** edit the original file.
   - Instead, document the correction in today's checkpoint and update the living `MASTER_RESEARCH_DOCUMENT.md` and relevant decision records.
3. **No Silent Changes**: Every transformation, file creation, code edit, and data operation must be documented with rationale, evidence, and validation results.
4. **Honesty About Failures**: Negative results, failed parsers, schema mismatches, and data unavailability are primary research findings. They must be explicitly documented under `Failed Investigations` and `Important Discoveries` to prevent redundant dead-end investigations.
5. **Actionable Next Starting Point**: The end of every checkpoint must provide a concrete, step-by-step starting point for the subsequent session. Vague statements such as "continue implementation" are strictly forbidden.

---

## 2. Standard Daily Checkpoint Schema

Every daily checkpoint must adhere to the following schema:

```markdown
# Research Checkpoint — YYYY-MM-DD

## Session Status
STATUS: SUCCESS / PARTIAL_SUCCESS / FAILED / BLOCKED / INVESTIGATION_ONLY

## Objective
[Clear description of what we intended to accomplish today]

## Work Completed
[Concrete, verified actions performed during this session]

## Verified Results
[Only facts, statistics, and outputs that were directly tested or observed]

## Successful Investigations
- **Problem**: ...
- **Method**: ...
- **Result**: ...
- **Evidence**: ...
- **Decision**: ...

## Failed Investigations
- **Attempted Approach**: ...
- **Why Attempted**: ...
- **What Happened**: ...
- **Evidence**: ...
- **Why It Failed**: ...
- **Retrial Recommendation**: ...

## Important Discoveries
[New knowledge discovered during the session]

## Decisions Made
[Architectural, dataset, or methodological decisions and rationale]

## Files Created
[List of new files created]

## Files Modified
[List of existing files modified]

## Files Deleted
[List of files deleted; if none, write NONE]

## Dataset State
[Exact measured state: row counts, missingness rates, hashes, blockers]

## Model State
[Exact state of architecture, layers, code, weights, training status]

## Documentation State
[Summary of documentation files created, updated, or reorganized]

## Unresolved Issues
[Living list of open questions, missing files, or blocked tasks]

## Next Starting Point
1. [First concrete task]
2. [Second concrete task]
3. [Third concrete task]

## Reproducibility Commands
[Exact shell/python commands executed to verify state]

## Evidence
[References to reports, code lines, logs, and datasets]
```
