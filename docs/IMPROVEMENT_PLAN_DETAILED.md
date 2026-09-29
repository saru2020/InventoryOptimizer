# Improvement Plan (detailed)

Short version: [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md). Evidence for everything below is in
[PROJECT_ANALYSIS_DETAILED.md](PROJECT_ANALYSIS_DETAILED.md). Item statuses refer to the pull request that
introduced these documents.

## P0 - security and correctness

### IMP-01 Move the Docker image to a supported Python release

- Category: security, upgrade
- Problem: at `98e48fb` the image was `python:3.8-slim` (`Dockerfile:2`). Python 3.8 has had no security fixes since
  its final release in October 2024, and pip resolves only old wheels there: pandas 2.0.3, numpy 1.24.4,
  scikit-learn 1.3.2, matplotlib 3.7.5, pillow 10.4.0. `pip-audit` inside that image reports PYSEC-2024-110 for
  scikit-learn (fixed in 1.5.0) and 17 advisories for pillow (the newest fixed in 12.3.0). See the Security section
  of the detailed analysis.
- Change: base the image on `python:3.12-slim`.
- Benefit: no project dependency with a known advisory, and the same versions the code is developed against.
- Effort: S. Risk: low - the resolved pandas 3.0.6 and numpy 2.5.3 are two majors ahead, so the suite must be run
  against them.
- Dependencies: none.
- Acceptance: `docker build` succeeds, `python test_inventory_optimization.py` passes inside the image, a container
  run writes 13 CSVs, and `pip-audit` reports no advisory for pandas, numpy, holidays, scikit-learn, matplotlib or
  pillow.
- Status: Addressed in this pull request. Verified: build, 36 tests passing and 13 CSVs on `python:3.12-slim`.

### IMP-02 Carry inventory forward instead of redrawing it

- Category: fix
- Problem: `generate_synthetic_data` sets `inventory_level = max(0, np.random.randint(10, 100))` for every row
  (`inventory_optimization.py:131`), independently of that store and SKU's sales, pending orders or deliveries.
  Every metric derived from stock level therefore describes noise: store turnover comes out around 244 on a default
  run against the roughly 2.0 the README shows, `DaysToStockout` jumps day to day, and `IsExcess` and `IsAtRisk`
  flip for reasons unrelated to demand.
- Change: simulate a stock position per store and SKU - opening stock, minus the day's sales, plus deliveries of
  orders whose lead time has elapsed, with reorders raised when the level crosses the reorder point. Keep the
  generator deterministic under `seed`.
- Benefit: the 16 metrics become internally consistent and the example numbers in the README become reproducible.
- Effort: M. Risk: medium - every metric's output changes, and several existing tests assert on row counts that will
  move.
- Dependencies: none, but IMP-07 (value tests) should land alongside so the new behaviour is pinned.
- Acceptance: store turnover falls in a plausible range (single digits) for the default configuration; inventory
  level never goes negative; a test asserts that closing stock equals opening stock minus sales plus deliveries for a
  sampled store and SKU.
- Status: Proposed.

### IMP-03 Reconcile documented formulas with the implementation

- Category: fix, documentation
- Problem: three documented formulas do not match the code.
  - Safety stock is documented as `Z-score × √(Lead Time) × Standard Deviation of Demand`
    (`METRICS_DOCUMENTATION.md:37`) but implemented as `1.96 × std(SalesQuantity)` with no lead time term
    (`inventory_optimization.py:205`). The lead time is available per row, so the documented version is computable.
  - Store turnover is documented as sales over average inventory *value* (README metrics table row 6) but computed
    over average inventory *level* (`inventory_optimization.py:279`).
  - Profitability is documented as profit per unit times total sales quantity but computed against the last row's
    `SalesQuantity` (`inventory_optimization.py:479`), a single day, while `ProfitabilityRatio` then divides by
    `TotalSales`.
- Change: for each, decide whether the document or the code is right, then change the other. Safety stock and
  profitability look like code defects; store turnover may be a deliberate simplification, in which case the README
  wording is what changes.
- Benefit: the metric reference can be trusted, and `ProfitabilityCategory` stops depending on which day happens to
  be last in the frame.
- Effort: S per metric. Risk: low for the documentation half, medium for the code half because output values move.
- Dependencies: none.
- Acceptance: every formula in `METRICS_DOCUMENTATION.md` matches the corresponding line of
  `inventory_optimization.py`, and a test pins one worked example per changed metric.
- Status: Proposed. The README metrics table rows 1 and 6 were corrected to describe the current implementation in
  this pull request, and each of the three sections in `METRICS_DOCUMENTATION.md` now records what the code actually
  does, so only the code-versus-document decision remains.

## P1 - high value

### IMP-04 Make the pre-commit lint hook pass

- Category: developer experience
- Problem: the `python-linting` hook runs `python -m flake8` with no configuration
  (`.pre-commit-config.yaml:15-20`). flake8 exits 1 with 365 findings on the two files it checks, 185 `W293` and 107
  `E501`. There is no `setup.cfg`, `tox.ini` or `pyproject.toml` to relax the defaults, so the hook blocks every
  commit unless it is skipped, and the black and isort hooks would reformat both files on their first run.
- Change: add a flake8 configuration with a line length matching the existing code, run black and isort once as a
  dedicated formatting commit, and confirm `pre-commit run --all-files` is clean.
- Benefit: the hooks do what they claim, and the formatting churn happens once in a reviewable commit instead of on
  someone's next commit.
- Effort: M, mostly the one-off reformat. Risk: low, but the reformat touches both files in full.
- Dependencies: best done after IMP-02 and IMP-03 to avoid conflicts with their code changes.
- Acceptance: `pre-commit run --all-files` exits 0 on a clean checkout; `python test_inventory_optimization.py`
  still passes afterwards.
- Status: Proposed.

### IMP-05 Pin dependencies

- Category: infrastructure
- Problem: `requirements.txt` gives lower bounds only and there is no lockfile, so the same command installs pandas
  2.0.3 on Python 3.8 and pandas 3.0.6 on Python 3.12. A pandas 3 behaviour change would surface as a mystery
  failure rather than a deliberate upgrade.
- Change: pin each dependency to the version the project is tested against, or add a lockfile, and state the
  supported Python range in the README.
- Benefit: reproducible installs, and upgrades become explicit commits.
- Effort: S. Risk: low.
- Dependencies: IMP-01, so the pins are taken from a supported interpreter.
- Acceptance: a fresh install from the pinned file produces the same versions on two machines, and the test suite
  passes against them.
- Status: Proposed.

### IMP-06 Continuous integration

- Category: developer experience
- Problem: no workflow existed at `98e48fb`, so nothing ran the 36 tests on a pull request.
- Change: a workflow on `ubuntu-latest` that installs `requirements.txt` and runs
  `python test_inventory_optimization.py` for pull requests and pushes to `main`, with `contents: read` permissions,
  concurrency cancellation and a timeout.
- Benefit: regressions are caught before merge.
- Effort: S. Risk: none.
- Dependencies: none.
- Acceptance: the workflow passes on this pull request; `actionlint` reports no problems.
- Status: Addressed in this pull request.

## P2 - worthwhile

### IMP-07 Tests for the output path and for metric values

- Category: testing
- Problem: coverage is 71% of `inventory_optimization.py` (294 statements, 85 missed). The uncovered part is
  `main()`, `save_metrics_to_csv()` and `print_metrics_summary()`, so nothing tests that 13 files are written, that
  the `/data` versus `data/` selection works, or that the CSVs have the expected headers. Separately, the existing
  assertions are structural - no test pins a computed number, so any formula change passes silently.
- Change: add tests that run `main()` against a temporary output directory and assert on the file set and headers,
  and add value assertions for safety stock, EOQ and reorder point on a small hand-built frame.
- Benefit: the formula changes in IMP-02 and IMP-03 become safe to make.
- Effort: M. Risk: low.
- Dependencies: `save_metrics_to_csv` already takes `output_dir`; `main()` does not, so it needs a parameter or the
  test needs to change working directory.
- Acceptance: coverage above 90%, and one test per core metric asserting an exact expected value.
- Status: Proposed.

### IMP-08 Remove dead code

- Category: fix
- Problem: `import csv` and four unused `typing` imports (`inventory_optimization.py:3`, `:10`) and the unused
  `service_level` variable (`:203`); `inventory_optimization_old.py` and `inventory_optimization_with_graph.py` are
  not imported, tested or referenced by the README, and the second writes to `/data` unconditionally so it only runs
  inside a container.
- Change: the imports and the variable are removed in this pull request. For the two legacy scripts, either delete
  them (the history keeps them) or move them under `examples/` with a line in the README saying what they are.
- Benefit: the root of the repository stops implying there are three pipelines.
- Effort: S. Risk: low.
- Dependencies: none.
- Acceptance: `flake8 --select=F` reports nothing; no unreferenced script sits at the repository root.
- Status: imports and variable Addressed in this pull request; the legacy scripts remain Proposed.

### IMP-09 Stop tracking generated output

- Category: infrastructure
- Problem: `data/` holds 14 tracked files (13 CSVs and `_plot_.png`) totalling 2.3 MB, all regenerated by every run,
  so every run dirties the working tree. The `.gitignore` entries that would exclude them are commented out.
- Change: uncomment the `data/` entries in `.gitignore` and untrack the files with `git rm --cached`. Adding to
  `.gitignore` alone does not untrack what is already committed. Keep one small sample if the README's example
  tables should stay reproducible.
- Benefit: clean diffs, smaller clones.
- Effort: S. Risk: low, but it is a deliberate decision about whether the sample output is part of the deliverable.
- Dependencies: none.
- Acceptance: `git status` is clean after a full pipeline run.
- Status: Proposed. Not done here because removing committed files is a call for the repository owner.

## P3 - longer term

### IMP-10 Vectorise the row-wise calculations

- Category: enhancement
- Problem: `calculate_reorder_point` and `calculate_daily_order` use `df.apply(..., axis=1)`
  (`inventory_optimization.py:228`, `:253`, `:259`). A default run (3,285 rows) takes 0.52 seconds, but 20 stores ×
  50 SKUs × 365 days (365,000 rows) takes 18.3 seconds, and those three calls dominate it.
- Change: replace them with `Series.isin`, `numpy.where` and `numpy.select`.
- Benefit: larger configurations become usable.
- Effort: S. Risk: low, and a value test from IMP-07 makes it verifiable.
- Dependencies: IMP-07.
- Acceptance: identical output for a fixed seed, measurably faster on the 365,000-row configuration.
- Status: Proposed.

### IMP-11 Accept real input data

- Category: enhancement
- Problem: `main()` always calls `generate_synthetic_data()` (`inventory_optimization.py:737`). The README suggests a
  `load_custom_data` function, but nothing in the code reads a user-supplied CSV.
- Change: add a command line interface that takes the generation parameters currently hardcoded in `main()` and
  optionally an input CSV path, validating the 13 required columns before running.
- Benefit: the tool becomes usable on real data, which is what the README's Advanced Usage section implies.
- Effort: M. Risk: medium - column types, missing values and date parsing all need handling that the synthetic path
  never exercises.
- Dependencies: IMP-07 for the validation tests.
- Acceptance: running against a supplied CSV produces the same 13 outputs; a malformed file fails with a clear
  message naming the missing column.
- Status: Proposed.

### IMP-12 Stop suppressing warnings globally

- Category: developer experience
- Problem: `warnings.filterwarnings('ignore')` at `inventory_optimization.py:11` and in the test module hides every
  deprecation warning, including the pandas 3 ones that would flag future breakage.
- Change: remove the blanket call, fix what it was hiding, and narrow any remaining suppression to a specific
  category and message.
- Benefit: upgrades stop being surprises.
- Effort: S once the warnings are known. Risk: low.
- Dependencies: IMP-05, so the pinned versions define which warnings matter.
- Acceptance: the suite passes with `-W error::DeprecationWarning`.
- Status: Proposed.

## Open issues

There are no open issues on the repository, so no plan item references one.

## Suggested order

- Quick wins: IMP-01 and IMP-06 (done here), IMP-08's import cleanup (done here), then IMP-05 and IMP-09.
- Next: IMP-07, then IMP-02 and IMP-03 with the value tests in place, then IMP-04 as a single formatting commit.
- Later: IMP-10, IMP-11, IMP-12.
