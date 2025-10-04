# Dicomization App

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-yes-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

A Flask web application for converting PDF/JPG/PNG files to **DICOM** and uploading them to **Orthanc**. Integrated with **Stone WebViewer**.

---

## Features

- Manual patient data input:
  - Patient ID (required)
  - Accession Number (optional)
  - First Name, Last Name
  - Date of Birth (DD-MM-YYYY)
  - Study Date (optional, defaults to file modification date)
  - Study Description
- Upload multiple files at once
- Automatic DICOM conversion (PDF, JPG, JPEG, PNG)
- Upload to Orthanc server via REST API
- Quick links:
  - Stone WebViewer
  - Orthanc Explorer

---

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local dev)
- `.env` file for sensitive credentials

---

## Setup

1. **Clone repository**
```bash
git clone https://github.com/dkortho/dicomization-app.git
cd dicomization-app
