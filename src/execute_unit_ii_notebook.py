"""Execute the saved Unit II notebook from the repository root."""

from pathlib import Path

import nbformat
from nbclient import NotebookClient


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "notebooks/01_exploracion_datos.ipynb"
    notebook = nbformat.read(path, as_version=4)
    NotebookClient(
        notebook,
        timeout=120,
        kernel_name="python3",
        resources={"metadata": {"path": str(root)}},
    ).execute()
    nbformat.write(notebook, path)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    errors = [
        output for cell in code_cells for output in cell.get("outputs", [])
        if output.output_type == "error"
    ]
    if errors:
        raise RuntimeError(f"Notebook terminó con {len(errors)} error(es)")
    print(f"Notebook ejecutado: {len(code_cells)} celdas de código; errores: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
