"""
ModelStorage local wrapper.

Drop-in replacement for the Zoho Analytics Code Studio ``ModelStorage``
module.  Stores and retrieves trained model artefacts (``*.pkl``) from
a local ``models/`` directory instead of Zoho's cloud storage.

Usage
-----
    from ModelStorage import ModelStorage

    ms = ModelStorage()
    ms.store_model("lead_conversion_pred_models", "/path/to/model.pkl")
    path = ms.get_model_path("lead_conversion_pred_models")
    ms.list_models()
"""

import json
import os
import shutil


class ModelStorage:
    """Local filesystem-backed model registry.

    The real Code Studio ``ModelStorage`` persists model files inside
    the Zoho Analytics workspace.  This wrapper stores them under a
    configurable local directory (default: ``crm/models/``).

    A lightweight JSON manifest (``_registry.json``) keeps track of
    model-name → file-path mappings, mirroring the remote registry.
    """

    def __init__(self, models_dir: str | None = None, logger=None):
        """
        Parameters
        ----------
        models_dir : str, optional
            Directory to store model files.  Defaults to
            ``<script_dir>/models``.
        logger : object, optional
            Logger with ``.INFO`` / ``.ERROR`` methods.  Falls back to
            plain ``print()`` if not supplied.
        """
        if models_dir is None:
            self._models_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "models"
            )
        else:
            self._models_dir = models_dir

        self._models_dir = os.path.normpath(self._models_dir)
        os.makedirs(self._models_dir, exist_ok=True)

        self._registry_path = os.path.join(self._models_dir, "_registry.json")
        self._registry: dict[str, str] = self._load_registry()
        self._log = logger

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _info(self, msg: str):
        if self._log:
            self._log.INFO(msg)
        else:
            print(f"[ModelStorage] {msg}")

    def _error(self, msg: str):
        if self._log:
            self._log.ERROR(msg)
        else:
            print(f"[ModelStorage ERROR] {msg}")

    def _load_registry(self) -> dict[str, str]:
        if os.path.isfile(self._registry_path):
            with open(self._registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_registry(self):
        with open(self._registry_path, "w", encoding="utf-8") as f:
            json.dump(self._registry, f, indent=2)

    # ------------------------------------------------------------------
    # Public API (matches Code Studio ModelStorage)
    # ------------------------------------------------------------------
    def store_model(self, model_name: str, source_path: str) -> None:
        """Register (and optionally copy) a model artefact.

        Parameters
        ----------
        model_name : str
            Logical name for the model (e.g. ``"lead_conversion_pred_models"``).
        source_path : str
            Path to the serialised model file (``.pkl``).  If the file is
            not already inside ``models_dir`` it will be copied there.
        """
        source_path = os.path.normpath(source_path)

        # If the source is outside models_dir, copy it in
        if not source_path.startswith(self._models_dir):
            dest = os.path.join(self._models_dir, os.path.basename(source_path))
            shutil.copy2(source_path, dest)
            stored_path = dest
        else:
            stored_path = source_path

        self._registry[model_name] = stored_path
        self._save_registry()
        self._info(f"Stored model '{model_name}' → {stored_path}")

    def get_model_path(self, model_name: str) -> str:
        """Return the filesystem path of a previously stored model.

        Parameters
        ----------
        model_name : str
            Logical name used during ``store_model``.

        Returns
        -------
        str
            Absolute path to the model file.

        Raises
        ------
        FileNotFoundError
            If the model name is unknown or the file has been deleted.
        """
        # Check registry first
        if model_name in self._registry:
            path = self._registry[model_name]
            if os.path.isfile(path):
                return path

        # Fallback: look for <model_name>.pkl in models_dir
        fallback = os.path.join(self._models_dir, f"{model_name}.pkl")
        if os.path.isfile(fallback):
            # Auto-register for future calls
            self._registry[model_name] = fallback
            self._save_registry()
            return fallback

        raise FileNotFoundError(
            f"Model '{model_name}' not found. "
            f"Searched registry and {self._models_dir}"
        )

    def list_models(self) -> list[str]:
        """Print and return all registered model names."""
        if not self._registry:
            self._info("No models registered yet.")
            return []

        self._info("Registered models:")
        for name, path in self._registry.items():
            exists = "✓" if os.path.isfile(path) else "✗ (missing)"
            self._info(f"  {name} → {path}  [{exists}]")

        return list(self._registry.keys())

    def delete_model(self, model_name: str) -> None:
        """Remove a model from the registry and delete the file."""
        if model_name in self._registry:
            path = self._registry.pop(model_name)
            if os.path.isfile(path):
                os.remove(path)
            self._save_registry()
            self._info(f"Deleted model '{model_name}'")
        else:
            self._error(f"Model '{model_name}' not in registry")
