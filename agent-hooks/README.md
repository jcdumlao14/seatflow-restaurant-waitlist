# SeatFlow Agent Guardrail

## Purpose
Run a read-only secret-pattern scan on explicitly selected files or staged Git
files, then run the SeatFlow structural-review capability tests.

## Usage
From the repository root:

```powershell
python agent-hooks/seatflow_guardrail.py --paths agent-capabilities/seatflow_review.py agent-capabilities/test_seatflow_review.py agent-hooks/seatflow_guardrail.py agent-hooks/test_seatflow_guardrail.py
python -m unittest discover -s agent-hooks -p "test_*.py" -v
python agent-hooks/seatflow_guardrail.py --staged
```

`--staged` inspects only paths already staged in Git. It does not stage files,
commit changes, execute application code, access the database, or change files.

## Safety and limitations
- Selected paths must remain inside the repository.
- Findings report labels and line numbers, never matched secret contents.
- This is a heuristic scan, not a complete secret detector or security audit.
- False positives and false negatives are possible.
- Do not use this tool as a substitute for a dedicated secret scanner.
- A nonzero exit code means a scan or verification step failed.