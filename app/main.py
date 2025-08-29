import os
import shutil
from fastapi import FastAPI, UploadFile, Depends
from fastapi.responses import FileResponse

from app.services.file_handler import handle_file_upload
from app.services.geospatial import get_crs, convert_to_dxf
from app.services.dxf_processor import process_dxf_labels
from app.models.schemas import ConvertToDxfParams, InspectResponse


app = FastAPI(
    title="Geospatial Converter API",
    description=(
        "API for inspecting and converting Shapefile"
        "or GeoPackage files to DXF, while preserving the coordinate system."
    ),
)

@app.get("/ping")
async def ping() -> dict[str, str]:
    """Health-check endpoint."""
    return {"status": "ok"}

@app.get("/")
async def root() -> dict[str, str]:
    """Test endpoint."""
    return {"message": "Hello World!"}

@app.post("/inspect/", response_model=InspectResponse)
async def inspect_file(file: UploadFile) -> InspectResponse:
    """Prikazuje osnovne informacije o geofajlu."""
    return await handle_file_upload(file, inspect=True)


@app.post("/convert-to-dxf/", response_class=FileResponse)
async def convert_to_dxf_endpoint(
    file: UploadFile,
    params: ConvertToDxfParams = Depends(),
) -> FileResponse:
    """
    Konvertuje Shapefile ili GeoPackage u DXF fajl
    sa očuvanim koordinatnim sistemom.
    """
    dataset_path, temp_dir = await handle_file_upload(file)

    try:
        srs = get_crs(dataset_path)
        output_path = convert_to_dxf(dataset_path, srs, params)
        process_dxf_labels(dataset_path, output_path, params)

        return FileResponse(
            output_path,
            media_type="application/dxf",
            filename=f"{params.output_name}.dxf",
        )
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
