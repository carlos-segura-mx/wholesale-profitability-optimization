"""Validate and unpack the public synthetic dataset.
Verifica y extrae el conjunto de datos sintéticos públicos.

Only approved files with known hashes are accepted.
Solo se aceptan archivos aprobados con huellas verificadas.
"""
import gzip
import hashlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "PORT01_PUBLIC_SYNTHETIC_DATA.zip"
EXPECTED = {
    "data/fact_sales.csv": "fef1740256420c4a2b968e6b11fb86e489a44285bfec773a1b88f9ec19b124b1",
    "data/fact_demand.csv": "4174da2cefc5fd8178486ff69f99b571480bcf12ceb8f170c26467faf6450b72",
    "data/fact_budget.csv": "dfba25d6365f665b4879e330986a964e85b55b20278e5dac45b42e2f5e7030c8",
    "data/fact_traffic.csv": "9c7f9709ac489d0e1d0e1eee61bb4930819410a0d648a5f5b24b6bdf875b82e5",
    "data/fact_operating_expense.csv": "4246d3f6f3174297ee10b8591769f37ae818e07fb93354de5aea0e1f95505a4b",
    "data/dim_product.csv": "d6bec8060049a0d8ff86e35e63d880e7c73a731e57d038383a334297767aa2b8",
    "data/dim_location.csv": "bb31e4dcfafc81c970d339b762b6df90b1e671af0663a8a3f1e8ff6940aa206a",
    "data/fact_inventory_snapshot.csv": "1bbdb75c76ee169b225d165f8d4b39dbc60480810708b58d319510950d9b8734",
    "data/fact_ticket.csv": "cdc2248546ead993aa7436a9a6789ede3f750bb722b3a28b61ad0c7a52f635c0",
    "data/fact_operations_monthly.csv": "e578f3e5419b7d55100c218f58d2289f08e41790bd1c74464b56b2ad7c2bbc24",
    "results_shelf_only/ticket_deltas.csv": "0d755b4e86f47d68338bad207e031f82c897f92378c12a2b2787bba8899e4393",
}

if not ARCHIVE.is_file():
    raise SystemExit("Missing archive / Falta el archivo: PORT01_PUBLIC_SYNTHETIC_DATA.zip")

with zipfile.ZipFile(ARCHIVE) as bundle:
    actual = {entry.filename for entry in bundle.infolist()}
    assert actual == set(EXPECTED), "Unexpected or missing paths / Rutas inesperadas o faltantes"
    for info in bundle.infolist():
        if info.file_size > 12_000_000:
            raise ValueError("File exceeds expected size / Archivo demasiado grande")
        data = bundle.read(info)
        signature = hashlib.sha256(data).hexdigest()
        if signature != EXPECTED[info.filename]:
            raise ValueError(f"SHA-256 mismatch / Diferencia de SHA-256: {info.filename}")
        target = ROOT / f"{info.filename}.gz"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(gzip.compress(data, compresslevel=9, mtime=0))
        print(f"OK {info.filename} ({len(data)} bytes)")

print("All datasets verified / Todos los archivos verificados")
