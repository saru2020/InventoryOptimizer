# Project Analysis

Inventory Optimizer is a single-file Python batch tool for retail inventory planning. It generates a year of synthetic
sales and stock data for a configurable set of stores and SKUs, then computes 16 inventory metrics (safety stock, EOQ,
reorder point, turnover, stock-out risk, movement classification and others) and writes 13 CSV files to `data/`. It
suits anyone who wants a worked reference for inventory formulas rather than a system to run against live stock data.

The pipeline is `inventory_optimization.py` (799 lines): pandas and numpy for the calculations, `holidays` for
country and state holiday effects on demand, and a Docker image that runs the script and mounts `data/` as a volume.
`test_inventory_optimization.py` holds 36 unittest cases covering 71% of the pipeline. Two earlier scripts,
`inventory_optimization_old.py` and `inventory_optimization_with_graph.py`, are kept as history and are not wired into
anything.

Top three risks:

1. Inventory levels are drawn at random each day and never reflect sales or deliveries, so turnover, stock-out risk
   and days-to-stock-out are not internally consistent.
2. The `python-linting` pre-commit hook fails on the current tree (365 flake8 findings), so commits are blocked or the
   hook is being skipped.
3. `METRICS_DOCUMENTATION.md` states formulas that the code does not implement, most visibly for safety stock.

To run it: `pip install -r requirements.txt` then `python inventory_optimization.py`, or `./run.sh` for the
containerised run. Both are covered in the README.

Full detail, including evidence and file references: [PROJECT_ANALYSIS_DETAILED.md](PROJECT_ANALYSIS_DETAILED.md).
