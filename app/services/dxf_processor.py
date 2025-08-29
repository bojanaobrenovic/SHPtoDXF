import ezdxf
from osgeo import ogr
from fastapi import HTTPException


def process_dxf_labels(dataset_path: str, output_path: str, params) -> None:
    """
    Dodaje labele u DXF fajl na osnovu izabranog atributa.
    Takođe premešta geometrije na poseban sloj sa definisanom bojom.

    :param dataset_path: Putanja do ulaznog geodataset fajla (SHP/GPKG).
    :param output_path: Putanja do izlaznog DXF fajla.
    :param params: Parametri za stilizaciju i atribut labeliranja.
    """
    # Otvaranje izvornog dataset-a
    dataset = ogr.Open(dataset_path)
    if dataset is None:
        raise HTTPException(status_code=400, detail="Ne mogu da otvorim dataset.")

    layer = dataset.GetLayer()

    # Učitavanje DXF fajla
    try:
        doc = ezdxf.readfile(output_path)
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Neuspešno učitavanje DXF fajla: {e}")

    msp = doc.modelspace()

    # Kreiranje sloja za geometriju (ako ne postoji)
    geometry_layer = "geometry"
    if geometry_layer not in doc.layers:
        doc.layers.new(geometry_layer, dxfattribs={"color": params.geometry_color})

    # Premestiti sve entitete sa "0" u "geometry"
    for entity in msp.query("*[layer=='0']"):
        entity.dxf.layer = geometry_layer
        entity.dxf.color = params.geometry_color

    # Sloj za tekst (naziv = atribut za labelu)
    text_layer = params.attribute_for_label
    if text_layer not in doc.layers:
        doc.layers.new(text_layer, dxfattribs={"color": params.text_color})

    # Provera postojanja atributa
    layer_defn = layer.GetLayerDefn()
    field_names = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]

    if params.attribute_for_label not in field_names:
        raise HTTPException(
            status_code=400,
            detail=f"Atribut '{params.attribute_for_label}' ne postoji u dataset-u.",
        )

    # Dodavanje labela za poligone
    for feature in layer:
        geom = feature.GetGeometryRef()
        if geom and geom.GetGeometryType() in [ogr.wkbPolygon, ogr.wkbMultiPolygon]:
            centroid = geom.Centroid()
            x, y = centroid.GetX(), centroid.GetY()
            value = feature.GetField(params.attribute_for_label)
            if value is not None:
                msp.add_text(
                    str(value),
                    dxfattribs={
                        "layer": text_layer,
                        "height": 2,
                        "color": params.text_color,
                        "insert": (x, y),
                    },
                )

    # Snimanje izmenjenog fajla
    doc.saveas(output_path)

    # Zatvaranje dataset-a
    dataset = None