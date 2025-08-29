FROM ghcr.io/osgeo/gdal:ubuntu-full-3.8.4

# Postavljamo radni direktorijum unutar kontejnera
WORKDIR /shp_to_dxf

# Kopiramo requirements i instaliramo zavisnosti
COPY requirements.txt .

RUN apt-get update && apt-get install -y python3-pip python3-dev build-essential \
    && rm -rf /var/lib/apt/lists/*


RUN pip install -r requirements.txt

# Kopiramo ceo projekat
COPY . .

# Otvaramo port (ako planiraš FastAPI docs)
EXPOSE 8000

# Startujemo FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
