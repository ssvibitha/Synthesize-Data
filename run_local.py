"""
Local runner for Zoho Analytics Code Studio ML scripts.

This script bootstraps the local wrappers (ZohoAnalytics,
DataTransformationUtil, ModelStorage) and runs the MLModel class from
any of the Code Studio scripts — no code changes needed in the ML files.

Usage
-----
    # Run Lead Conversion (fit + predict)
    python run_local.py LeadConversionZA_v6 --fit --predict

    # Run Account Health Score (fit only)
    python run_local.py AccountsHealthScore --fit

    # Run Account Health Score (predict only, using previously trained model)
    python run_local.py AccountsHealthScore --predict

    # Run both by default if no flags given
    python run_local.py AccountsHealthScore
"""

import argparse
import importlib
import os
import sys
import time

# Ensure the crm/ directory is on sys.path so that the local wrappers
# are found when ML scripts do ``from ZohoAnalytics import ZohoAnalytics``
CRM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crm")
if CRM_DIR not in sys.path:
    sys.path.insert(0, CRM_DIR)

# Now import our local wrappers
from ZohoAnalytics import ZohoAnalytics  # noqa: E402
from ModelStorage import ModelStorage      # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Run Zoho Analytics Code Studio ML scripts locally.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python run_local.py AccountsHealthScore --fit --predict\n"
            "  python run_local.py LeadConversionZA_v6 --fit\n"
            "  python run_local.py AccountHealthScore --predict\n"
        ),
    )
    parser.add_argument(
        "script",
        help="Name of the ML script module in crm/ (without .py extension).",
    )
    parser.add_argument(
        "--fit",
        action="store_true",
        help="Run the training (fit) phase.",
    )
    parser.add_argument(
        "--predict",
        action="store_true",
        help="Run the prediction phase.",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Override the data directory (default: ./data).",
    )
    args = parser.parse_args()

    # If neither --fit nor --predict is specified, run both
    if not args.fit and not args.predict:
        args.fit = True
        args.predict = True

    # ── Bootstrap wrappers ─────────────────────────────────────────────
    za = ZohoAnalytics()
    ms = ModelStorage(logger=za.context.log)

    log = za.context.log

    # ── Dynamically import the target ML script ────────────────────────
    log.INFO(f"Loading ML script: crm/{args.script}.py")
    try:
        module = importlib.import_module(args.script)
    except ModuleNotFoundError as exc:
        log.ERROR(f"Could not import '{args.script}': {exc}")
        log.ERROR(f"Make sure '{args.script}.py' exists in {CRM_DIR}")
        sys.exit(1)

    # All scripts expose ``class MLModel`` with __init__(za, ms)
    ml_class = getattr(module, "MLModel", None)
    if ml_class is None:
        log.ERROR(f"'{args.script}' does not define an MLModel class.")
        sys.exit(1)

    model = ml_class(za, ms)

    # ── Run phases ─────────────────────────────────────────────────────
    print("=" * 60)
    print(f"  LOCAL RUNNER — {args.script}")
    print("=" * 60)

    if args.fit:
        print()
        log.INFO("▶ Starting FIT phase …")
        t0 = time.perf_counter()
        model.fit()
        elapsed = time.perf_counter() - t0
        log.INFO(f"✔ FIT completed in {elapsed:.1f}s")

    if args.predict:
        print()
        log.INFO("▶ Starting PREDICT phase …")
        t0 = time.perf_counter()
        model.predict()
        elapsed = time.perf_counter() - t0
        log.INFO(f"✔ PREDICT completed in {elapsed:.1f}s")

    print()
    print("=" * 60)
    print("  Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
