"""Execute a Unit III notebook from the project root and keep its outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def execute(root: Path, relative_path: str) -> int:
    path = root / relative_path
    notebook = nbformat.read(path, as_version=4)
    # Give every cell a stable nbformat ID before execution. This keeps the
    # persisted artifact valid for current Jupyter tooling and avoids warnings.
    for index, cell in enumerate(notebook.cells):
        cell.setdefault("id", f"unit3-cell-{index:03d}")
    nbformat.validate(notebook)
    NotebookClient(
        notebook, timeout=1800, kernel_name="python3",
        resources={"metadata": {"path": str(root)}},
    ).execute()
    errors = [
        output for cell in notebook.cells if cell.cell_type == "code"
        for output in cell.get("outputs", []) if output.output_type == "error"
    ]
    if errors:
        raise RuntimeError(f"Notebook {relative_path} generó {len(errors)} errores")
    nbformat.write(notebook, path)
    print(f"Notebook ejecutado: {relative_path}; errores=0")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", choices=["regresion", "clasificacion", "optimizacion"])
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    relative = {
        "regresion": "notebooks/02_regresion.ipynb",
        "clasificacion": "notebooks/03_clasificacion.ipynb",
        "optimizacion": "notebooks/04_optimizacion.ipynb",
    }[args.notebook]
    return execute(root, relative)


if __name__ == "__main__":
    raise SystemExit(main())
