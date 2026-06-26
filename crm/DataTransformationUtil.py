"""
DataTransformationUtil local wrapper.

Drop-in replacement for the Zoho Analytics Code Studio
``DataTransformationUtil`` module.  Reads/writes local CSV files in the
``data/`` directory instead of calling the Zoho Analytics REST API.

Usage
-----
    from DataTransformationUtil import DataTransformationUtil

    dt = DataTransformationUtil(za)          # za = ZohoAnalytics()
    df = dt.fetch_tabledata_as_DataFrame("ML_Query_Table", cols, "")
    dt.upload_tabledata_from_DataFrame("prediction_algorithms", df, opts)
"""

import os
import pandas as pd


class DataTransformationUtil:
    """Local CSV-backed replacement for ZA's DataTransformationUtil.

    The real Code Studio version talks to the Zoho Analytics API; this
    wrapper looks up CSV files by *table name* under a configurable data
    directory (defaults to ``../data/`` relative to this script).

    Table-name → file resolution
    ----------------------------
    Given a table name like ``"ML_Query_Table"``, the wrapper tries these
    file names in order (first match wins):

        1. ``ML_Query_Table.csv``           — exact match
        2. Any ``*.csv`` whose stem contains the table name (case-insensitive)

    This keeps the wrapper flexible without requiring rigid naming.
    """

    def __init__(self, za, data_dir: str | None = None):
        """
        Parameters
        ----------
        za : ZohoAnalytics
            The local ``ZohoAnalytics`` instance (used for logging).
        data_dir : str, optional
            Override for the directory that contains CSV files.  Defaults to
            ``<script_dir>/../data``.
        """
        self.za = za
        self.log = za.context.log

        if data_dir is None:
            self._data_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "data"
            )
        else:
            self._data_dir = data_dir

        self._data_dir = os.path.normpath(self._data_dir)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve_csv_path(self, table_name: str) -> str:
        """Resolve a logical table name to a CSV file path.

        Resolution order:
            1. Exact match  → ``<data_dir>/<table_name>.csv``
            2. Fuzzy match  → first ``*.csv`` whose stem contains ``table_name``
               (case-insensitive)

        Raises ``FileNotFoundError`` if no file can be found.
        """
        # 1. Exact match
        exact = os.path.join(self._data_dir, f"{table_name}.csv")
        if os.path.isfile(exact):
            return exact

        # 2. Fuzzy match
        lower = table_name.lower()
        for fname in sorted(os.listdir(self._data_dir)):
            if fname.lower().endswith(".csv") and lower in fname.lower():
                return os.path.join(self._data_dir, fname)

        raise FileNotFoundError(
            f"No CSV file found for table '{table_name}' in {self._data_dir}. "
            f"Expected '{table_name}.csv' or a file whose name contains '{table_name}'."
        )

    # ------------------------------------------------------------------
    # Public API (matches Code Studio DataTransformationUtil)
    # ------------------------------------------------------------------
    def fetch_tabledata_as_DataFrame(
        self,
        table_name: str,
        columns: list[str],
        criteria: str,
    ) -> pd.DataFrame:
        """Read a CSV file and return it as a ``pandas.DataFrame``.

        Parameters
        ----------
        table_name : str
            Logical table name (maps to a CSV file under ``data_dir``).
        columns : list[str]
            Columns to keep.  If empty, all columns are returned.
        criteria : str
            SQL WHERE clause (ignored locally; included for API compat).

        Returns
        -------
        pd.DataFrame
        """
        csv_path = self._resolve_csv_path(table_name)
        self.log.INFO(f"Reading table '{table_name}' from {csv_path}")

        df = pd.read_csv(csv_path)

        if columns:
            # Keep only columns that actually exist in the file
            valid = [c for c in columns if c in df.columns]
            missing = set(columns) - set(valid)
            if missing:
                self.log.WARNING(
                    f"Columns not found in '{table_name}' and skipped: {missing}"
                )
            df = df[valid]

        self.log.INFO(
            f"Loaded {len(df)} rows × {len(df.columns)} columns from '{table_name}'"
        )
        return df

    def upload_tabledata_from_DataFrame(
        self,
        table_name: str,
        df: pd.DataFrame,
        options: dict | None = None,
    ) -> None:
        """Write a ``DataFrame`` to a CSV file (simulates Zoho upload).

        Parameters
        ----------
        table_name : str
            Logical table name — used as the output CSV filename.
        df : pd.DataFrame
            Data to write.
        options : dict, optional
            Options dict (e.g. ``{"importType": "truncateadd"}``).
            - ``"truncateadd"`` → overwrite the file (default behaviour).
            - ``"append"``      → append rows to existing file.
        """
        options = options or {}
        import_type = options.get("importType", "truncateadd")

        out_path = os.path.join(self._data_dir, f"{table_name}.csv")

        if import_type == "append" and os.path.isfile(out_path):
            df.to_csv(out_path, mode="a", header=False, index=False)
            self.log.INFO(
                f"Appended {len(df)} rows to '{table_name}' → {out_path}"
            )
        else:
            df.to_csv(out_path, index=False)
            self.log.INFO(
                f"Wrote {len(df)} rows to '{table_name}' → {out_path}"
            )
