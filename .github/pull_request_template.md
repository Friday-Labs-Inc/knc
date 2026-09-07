## What

## Why
Closes #

## How it was verified
- [ ] Gate green locally — paste the summary line from `python ci/run_tests.py --site … --app design_studio --known-red ci/known-red.txt`
- [ ] `bench --site … migrate` clean
- [ ] `code-reviewer` and `security-reviewer` run; every CRITICAL/HIGH fixed (list any MEDIUM left open)
- [ ] Touched a known-red module? It is green and removed from `ci/known-red.txt`
- [ ] Nothing in this PR adds ERPNext/business logic to the friday kernel

## Migration / operator notes

## Design docs touched
