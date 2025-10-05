# Dicomization App

A Flask application to convert uploaded PDF or image files into DICOM format and upload them to an Orthanc server, with optional viewing in Stone WebViewer. Supports multiple files per study.

## Features

1. Manual input of patient information: Patient ID (required), Accession Number (optional), First Name, Last Name, Date of Birth (DD-MM-YYYY), Study Date (DD-MM-YYYY), Study Description
2. Upload multiple PDF or image files simultaneously
3. Convert files to DICOM using the provided patient information
4. Automatically generate Study UID for multiple file uploads
5. Upload converted DICOM files to an Orthanc server
6. View uploaded study in Stone WebViewer and open Orthanc Explorer via links
7. Environment variables used for sensitive configuration (Orthanc URL, credentials, Stone URL)

## Screenshot

![Dicomization App Screenshot](UI.png)

## Prerequisites

- Docker
- Docker Compose
- Git

## Setup

1. Clone the repository:

```
git clone https://github.com/YOUR_USERNAME/dicomization-app.git
cd dicomization-app
```

2. Create a `.env` file in the project root:

```
touch .env
```

3. Add the following environment variables to `.env`:

```
ORTHANC_API_URL=http://192.168.1.119:8042/instances #put your own
ORTHANC_EXPLORER_URL=http://192.168.1.119:8042/ #put your own
STONE_URL=https://orthanc.dkortho.synology.me:4445/stone-webviewer #put your own
ORTHANC_USER=your_orthanc_username
ORTHANC_PASS=your_orthanc_password
```

4. Ensure `.env` is in `.gitignore` to prevent exposing credentials.

## Docker Setup

1. Build and start the app using Docker Compose:

```
docker-compose up --build -d
```

2. The app will be accessible at `http://localhost:8017` (or your mapped port).

3. Verify logs:

```
docker-compose logs -f dicom_app
```

## 🩻 Dicomization App + Orthanc

Example usage with **Docker Compose** to run dicomization-app together with Orthanc, Orthanc Explorer 2, and Stone WebViewer.

**Docker Compose**

```
version: "3.9"

services:
  orthanc:
    image: orthancteam/orthanc:25.10.2
    container_name: orthancdicomizer
    ports:
      - "8044:8042"  # Orthanc REST API
      - "4244:4242"  # DICOM port
    volumes:
      - orthanc_data:/var/lib/orthanc/db
      - orthanc_config:/etc/orthanc
    restart: unless-stopped
    environment:
      ORTHANC__USER: "orthanc"
      ORTHANC__PASSWORD: "orthanc"
      STONE_WEB_VIEWER_PLUGIN_ENABLED: "true"
      DICOM_WEB_PLUGIN_ENABLED: |
        {
          "DicomWeb": {
            "Enable": true,
            "PublicRoot": "/orthanc/dicom-web/"
          }
        }
      ORTHANC_JSON: |
        {
          "Name": "Dicomization Server",
          "StandardConfigurations": [
            "stone-webviewer",
            "orthanc-explorer-2"
          ],
          "BuiltinDecoderTranscoderOrder" : "After",
          "OrthancExplorer2": {
            "Enable": true,
            "IsDefaultOrthancUI": true,
            "ShowOrthancName": true,
            "UiOptions": {
              "DateFormat": "ddMMyyyy",
              "StudyListColumns": [
                "AccessionNumber",
                "PatientName",
                "PatientBirthDate",
                "PatientID",
                "StudyDescription",
                "StudyDate",
                "modalities",
                "seriesCount"
              ]
            }
          },
          "RegisteredUsers": { "orthanc": "orthanc" },
          "StoneWebViewer": {
            "DateFormat": "DD/MM/YYYY",
            "ShowNotForDiagnosticUsageDisclaimer": false,
            "ShowInfoPanelAtStartup": "Never"
          },
          "OHIF": {
            "DataSource": "dicom-web"
          }
        }

  dicom_app:
    image: 788773/dicomization-app:latest
    container_name: dicom_app
    ports:
      - "8017:8000"
    environment:
      ORTHANC_API_URL: "http://192.168.1.105:8044/instances"
      ORTHANC_EXPLORER_URL: "http://192.168.1.105:8044"
      STONE_URL: "http://192.168.1.105:8044/stone-webviewer"
      ORTHANC_USER: "orthanc"
      ORTHANC_PASS: "orthanc"
    depends_on:
      - orthanc
    restart: unless-stopped

volumes:
  orthanc_data:
  orthanc_config:

```

## Usage

1. Open the app in your browser at `http://localhost:8017`.
2. Fill in the patient information form.
3. Select one or more files (PDF or JPG/PNG images) to upload.
4. Click **Upload DICOM**.
5. After successful upload, the results panel will show: number of files uploaded, names of uploaded files, link to Stone WebViewer for the study, link to Orthanc Explorer.

## Project Structure

dicomization-app/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── uploads/
└── .env


## Notes

- The `uploads/` directory should remain empty and can contain a `.gitkeep` file for Git tracking if needed.
- Always use environment variables for credentials; do not commit `.env` to version control.
- Multiple file uploads share the same Study UID, allowing them to be grouped as a single study in Orthanc.

## License

MIT License
