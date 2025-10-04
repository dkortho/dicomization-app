from flask import Flask, render_template, request, jsonify
import os
import uuid
import requests
from datetime import datetime
from PIL import Image
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset

app = Flask(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --------- Orthanc settings from environment ---------
ORTHANC_API_URL = os.environ.get("ORTHANC_API_URL")            # REST API endpoint (/instances)
ORTHANC_EXPLORER_URL = os.environ.get("ORTHANC_EXPLORER_URL")  # Orthanc Explorer UI
STONE_URL = os.environ.get("STONE_URL")                        # Stone viewer URL
ORTHANC_USER = os.environ.get("ORTHANC_USER")
ORTHANC_PASS = os.environ.get("ORTHANC_PASS")

# ------------- Helpers -------------
def parse_date_ddmmyyyy(date_str, fallback=None):
    """Convert DD-MM-YYYY to DICOM YYYYMMDD"""
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%d-%m-%Y")
            return dt.strftime("%Y%m%d")
        except:
            pass
    if fallback:
        return fallback.strftime("%Y%m%d")
    return ""

def dicomize_file(patient, filepath, study_uid=None):
    filename = os.path.basename(filepath)
    ext = filename.lower().split('.')[-1]

    sop_uid = pydicom.uid.generate_uid()
    if not study_uid:
        study_uid = pydicom.uid.generate_uid()
    series_uid = pydicom.uid.generate_uid()

    ds = Dataset()
    ds.SpecificCharacterSet = "ISO_IR 192"
    ds.PatientName = f"{patient['surname']}^{patient['name']}"
    ds.PatientID = patient['patient_id']
    ds.AccessionNumber = patient.get("accession", "")
    ds.PatientBirthDate = parse_date_ddmmyyyy(patient.get("dob", ""))

    ds.StudyInstanceUID = study_uid
    ds.SeriesInstanceUID = series_uid
    ds.SOPInstanceUID = sop_uid

    # Study date
    if patient.get("study_day"):
        ds.StudyDate = parse_date_ddmmyyyy(patient["study_day"])
    else:
        file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        ds.StudyDate = file_mtime.strftime("%Y%m%d")

    ds.ContentDate = datetime.now().strftime("%Y%m%d")
    ds.ContentTime = datetime.now().strftime("%H%M%S")
    if patient.get("study_description"):
        ds.StudyDescription = patient["study_description"]

    # Encapsulation
    if ext == "pdf":
        ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.104.1"
        ds.Modality = "DOC"
        with open(filepath, "rb") as f:
            ds.EncapsulatedDocument = f.read()
        ds.MIMETypeOfEncapsulatedDocument = "application/pdf"
    elif ext in ["jpg", "jpeg", "png"]:
        ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.7"
        ds.Modality = "XC"
        img = Image.open(filepath).convert("RGB")
        arr = np.array(img)
        ds.Rows, ds.Columns, _ = arr.shape
        ds.SamplesPerPixel = 3
        ds.PhotometricInterpretation = "RGB"
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.PixelData = arr.tobytes()
    else:
        raise ValueError("Unsupported file type")

    dicom_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.dcm")
    file_ds = FileDataset(dicom_path, {}, file_meta=FileMetaDataset(), preamble=b"\0" * 128)
    file_ds.update(ds)
    file_ds.is_little_endian = True
    file_ds.is_implicit_VR = False
    file_ds.save_as(dicom_path)
    return dicom_path, study_uid

# ------------- Routes -------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/dicomize_upload", methods=["POST"])
def dicomize_upload():
    patient = {
        "accession": request.form.get("accession", ""),
        "patient_id": request.form.get("patient_id", ""),
        "name": request.form.get("name", ""),
        "surname": request.form.get("surname", ""),
        "dob": request.form.get("dob", ""),
        "study_description": request.form.get("study_description", ""),
        "study_day": request.form.get("study_day", "")
    }

    files = request.files.getlist("file")
    if not files:
        return jsonify({"error": "No files selected"}), 400

    study_uid = None
    success_count = 0

    for f in files:
        filepath = os.path.join(UPLOAD_DIR, f.filename)
        f.save(filepath)

        dicom_path, study_uid = dicomize_file(patient, filepath, study_uid)

        try:
            with open(dicom_path, "rb") as dcm:
                r = requests.post(
                    ORTHANC_API_URL,
                    data=dcm,
                    headers={"Content-Type": "application/dicom"},
                    auth=(ORTHANC_USER, ORTHANC_PASS),
                    timeout=15
                )
            if r.status_code in range(200, 300):
                success_count += 1
            else:
                print(f"Orthanc returned {r.status_code} for {f.filename}")
        except Exception as e:
            print(f"Error uploading {f.filename}:", str(e))

    # Links
    stone_link = f"{STONE_URL.rstrip('/')}/index.html?study={study_uid}" if STONE_URL else None
    orthanc_explorer_link = ORTHANC_EXPLORER_URL

    return jsonify({
        "status": 200,
        "message": f"{success_count} of {len(files)} files uploaded successfully",
        "study_uid": study_uid,
        "stone_link": stone_link,
        "orthanc_explorer_link": orthanc_explorer_link,
        "files": [f.filename for f in files]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
