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

## Usage

1. Open the app in your browser at `http://localhost:8017`.
2. Fill in the patient information form.
3. Select one or more files (PDF or JPG/PNG images) to upload.
4. Click **Upload DICOM**.
5. After successful upload, the results panel will show: number of files uploaded, names of uploaded files, link to Stone WebViewer for the study, link to Orthanc Explorer.

## Project Structure

```
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
```

## Notes

- The `uploads/` directory should remain empty and can contain a `.gitkeep` file for Git tracking if needed.
- Always use environment variables for credentials; do not commit `.env` to version control.
- Multiple file uploads share the same Study UID, allowing them to be grouped as a single study in Orthanc.

## License

MIT License
