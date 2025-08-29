import os
import zipfile
import tempfile
from fastapi import UploadFile, HTTPException
from osgeo import ogr, gdal

gdal.SetConfigOption("SHAPE_RESTORE_SHX", "YES")
ogr.UseExceptions()

SHAPEFILE_EXTS = [".shp", ".shx", ".dbf", ".prj", ".cpg"]


async def handle_file_upload(file: UploadFile, inspect: bool = False):
    """
    Obrada uploadovanog fajla (.zip sa Shapefile-om ili .gpkg).

    Ako je `inspect=True`, vraća informacije o dataset-u.
    Inače vraća putanju do dataset-a i temp direktorijum
    (koji korisnik mora ručno obrisati nakon obrade).
    """
    filename = file.filename.lower()

    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file.filename)

    with open(input_path, "wb") as f:
        f.write(await file.read())

    if filename.endswith(".zip"):
        try:
            with zipfile.ZipFile(input_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Neispravan .zip fajl")

        dataset_path = next(
            (os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.lower().endswith(".shp")),
            None
        )
        if not dataset_path:
            raise HTTPException(status_code=400, detail="Nije pronađen .shp fajl u zip-u")

    elif filename.endswith(".gpkg"):
        dataset_path = input_path

    else:
        raise HTTPException(status_code=400, detail="Uploadujte .zip (shapefile) ili .gpkg fajl")

    if not os.path.exists(dataset_path):
        raise HTTPException(status_code=400, detail=f"Fajl ne postoji: {dataset_path}")

    if inspect:
        dataset = ogr.Open(dataset_path)
        if dataset is None:
            raise HTTPException(status_code=400, detail=f"Ne mogu otvoriti fajl: {dataset_path}")

        layer = dataset.GetLayer()
        layer_defn = layer.GetLayerDefn()

        fields = [
            layer_defn.GetFieldDefn(i).GetName()
            for i in range(layer_defn.GetFieldCount())
        ]
        geometry_type = ogr.GeometryTypeToName(layer_defn.GetGeomType())
        feature_count = layer.GetFeatureCount()

        srs = layer.GetSpatialRef()
        crs_info = None
        if srs:
            try:
                epsg = srs.GetAuthorityCode(None)
            except Exception:
                epsg = None
            crs_info = {
                "epsg": epsg,
                "proj4": srs.ExportToProj4()
            }

        dataset = None

        return {
            "filenames": os.listdir(temp_dir),
            "geometry_type": geometry_type,
            "feature_count": feature_count,
            "fields": fields,
            "crs": crs_info,
        }

    return dataset_path, temp_dir
