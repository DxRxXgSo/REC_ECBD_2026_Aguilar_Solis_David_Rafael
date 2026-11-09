"""Execute the U2 AE1 notebook and persist its outputs after a clean run."""

from __future__ import annotations

import json
import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks/Aguilar_Solis_David_Rafael_U2_AE1_Exploracion.ipynb"


def main() -> int:
    if not NOTEBOOK.is_file():
        raise FileNotFoundError(f"No existe el notebook requerido: {NOTEBOOK}")

    notebook = nbformat.read(NOTEBOOK, as_version=4)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    if not code_cells:
        raise ValueError("El notebook no contiene celdas de código para ejecutar.")

    os.chdir(NOTEBOOK.parent)
    client = NotebookClient(
        notebook,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(NOTEBOOK.parent)}},
    )
    client.execute()

    errors = [
        output
        for cell in notebook.cells
        if cell.cell_type == "code"
        for output in cell.get("outputs", [])
        if output.output_type == "error"
    ]
    if errors:
        raise RuntimeError(f"La ejecución produjo {len(errors)} error(es).")
    nbformat.write(notebook, NOTEBOOK)

    figure_outputs = sum(
        1
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.output_type in {"display_data", "execute_result"}
        and any(key in output.get("data", {}) for key in ("image/png", "image/jpeg", "image/svg+xml"))
    )
    print(json.dumps({
        "notebook": str(NOTEBOOK),
        "code_cells": len(code_cells),
        "executed_cells": sum(cell.execution_count is not None for cell in code_cells),
        "errors": len(errors),
        "figure_outputs": figure_outputs,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
