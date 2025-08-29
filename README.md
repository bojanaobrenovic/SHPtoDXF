# SHP to DXF FastAPI Application

This application is primarily designed for **geospatial data**, such as cadastral parcels.
It allows converting Shapefile (.shp) files to **DXF format (sxf)**, which can be easily imported into CAD software.
The app is built with FastAPI and GDAL, containerized using Docker, and ready for local testing.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- Windows, MacOS, or Linux
- Project folder containing the FastAPI app

---

## Running the Application

1. Open a terminal in the project root folder (`shp_to_dxf`).

2. Build the Docker image:

```bash
docker-compose build 
```

3.Start the application:
```bash
docker-compose up
```
4. To run in detached mode (background):
```bash
docker-compose up
```
5. To stop the application:
```bash
docker-compose down
```

## Uploading and Converting Files
 #### Important: Shapefile and all associated files must be uploaded as a ZIP archive.

The local data/ folder is mounted inside the container, so all files placed there are accessible by the app.

Uploaded ZIP files containing shapefiles are extracted and converted to DXF format (sxf) for easy import into CAD software

## Testing the Application
- FastAPI interactive documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
