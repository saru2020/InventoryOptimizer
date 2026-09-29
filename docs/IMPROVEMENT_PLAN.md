# Improvement Plan

The five things worth doing next, in order. Full detail, including evidence and acceptance criteria, is in
[IMPROVEMENT_PLAN_DETAILED.md](IMPROVEMENT_PLAN_DETAILED.md).

1. **IMP-01 - Run on a supported Python.** The Docker image was built on `python:3.8-slim`, which pulled
   scikit-learn 1.3.2 and pillow 10.4.0, both carrying known advisories. Addressed in this pull request.
2. **IMP-02 - Make inventory levels follow the simulation.** `InventoryLevel` is a fresh random draw each day, so
   turnover, stock-out risk and days-to-stock-out are not internally consistent. Carrying stock forward from sales
   and deliveries is what makes every stock-derived metric meaningful.
3. **IMP-03 - Reconcile the documented formulas with the code.** Safety stock, store turnover and profitability are
   described one way in `METRICS_DOCUMENTATION.md` and computed another way. Decide which is correct for each, then
   change the code or the document.
4. **IMP-04 - Make the pre-commit lint hook pass.** `flake8` exits 1 with 365 findings, so the `python-linting` hook
   blocks every commit unless it is skipped. It needs a configuration and a one-off whitespace cleanup.
5. **IMP-05 - Pin dependencies and test the output path.** `requirements.txt` has lower bounds only, and `main()`,
   `save_metrics_to_csv()` and `print_metrics_summary()` are the 29% of the pipeline no test touches.

Two smaller items from this pull request are already done: the test script now exits non-zero on failure and a test
workflow runs on pull requests and pushes to `main` (IMP-06), and the unused imports and variable are gone (IMP-08).
