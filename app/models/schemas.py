from typing import Optional
from pydantic import BaseModel


class ConvertToDxfParams(BaseModel):
    """
    Parametri za konverziju u DXF.
    """
    attribute_for_label: str
    geometry_color: int = 7
    text_color: int = 7
    output_name: str = "output"
    output_dir: str


class InspectResponse(BaseModel):
    """
    Odgovor za inspekciju geofajla.
    """
    filenames: list[str]
    geometry_type: str
    feature_count: int
    fields: list[str]
    crs: Optional[dict]
