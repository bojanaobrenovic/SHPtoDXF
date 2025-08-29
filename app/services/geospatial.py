import os
import subprocess
import logging
import geopandas as gpd
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def get_crs(dataset_path: str) -> str:
    """
    Vraća koordinatni referentni sistem (CRS) za dati dataset.

    Args:
        dataset_path (str): Putanja do fajla (Shapefile ili GeoPackage).

    Returns:
        str: CRS u WKT/PROJ4 string formatu.

    Raises:
        HTTPException: Ako fajl ne postoji ili nema definisan CRS.
    """
    if not os.path.exists(dataset_path):
        raise HTTPException(
            status_code=400,
            detail=f"Fajl ne postoji na putanji: {dataset_path}"
        )

    try:
        logger.info("Učitavanje fajla: %s", dataset_path)
        gdf = gpd.read_file(dataset_path)

        if gdf.crs is None:
            raise HTTPException(
                status_code=400,
                detail="Ulazni fajl nema definisan koordinatni sistem"
            )

        return gdf.crs.to_string()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Greška pri čitanju koordinatnog sistema: {exc}"
        ) from exc


def convert_to_dxf(dataset_path: str, srs: str, params) -> str:
    """
    Konvertuje dataset u DXF format pomoću ogr2ogr.

    Args:
        dataset_path (str): Putanja do ulaznog dataset-a.
        srs (str): Koordinatni sistem (npr. EPSG:4326).
        params: Parametri za izlaz (output_dir, output_name).

    Returns:
        str: Putanja do izlaznog DXF fajla.

    Raises:
        HTTPException: Ako dođe do greške u konverziji.
    """
    output_path = os.path.join(params.output_dir, f"{params.output_name}.dxf")
    os.makedirs(params.output_dir, exist_ok=True)

    try:
        logger.info("Pokrećem ogr2ogr konverziju u DXF: %s", output_path)

        subprocess.run(
            [
                "ogr2ogr",
                "-f", "DXF",
                output_path,
                dataset_path,
                "-nln", "geometry",
                "-s_srs", srs,
                "-t_srs", srs,
                "-dim", "XY",
                "-nlt", "MULTILINESTRING"
            ],
            check=True,
            timeout=30
        )
        return output_path

    except subprocess.CalledProcessError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Greška u konverziji: {exc}"
        ) from exc

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=500,
            detail="Konverzija je istekla"
        )
