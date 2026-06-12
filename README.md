# 📊 CAS_to_Spreadsheet

**CAS_to_Spreadsheet** is a Python-based offline parser that converts Consolidated Account Statements (CAS) into Excel spreadsheets with an easy-to-use UI for non-technical users.

It supports both **CAMS** and **KFintech** CAS statements in **Summary and Detailed formats**.

---

## 🚀 Features

* 📄 Parse CAS statements (PDF format)
* 🧾 Supports both:

  * CAMS CAS (Summary & Detailed)
  * KFintech CAS (Summary & Detailed)
* 📊 Export data to Excel (.xlsx)
* 🖥️ Simple web-based UI (browser interface)
* 🔌 Fully offline after setup
* 👨‍💻 Designed for non-technical users

---
## ScreenShot
<img width="1604" height="705" alt="image" src="https://github.com/user-attachments/assets/f58aaab4-614e-4207-b59a-e2711233b09b" />
<img width="1187" height="601" alt="image" src="https://github.com/user-attachments/assets/561820fa-6b10-4562-9edc-2ec6f7a8561b" />
<img width="1220" height="511" alt="image" src="https://github.com/user-attachments/assets/ecc2be77-9b5b-4cef-a851-bd91bdfb8775" />
<img width="1031" height="201" alt="image" src="https://github.com/user-attachments/assets/2dc60298-eda7-4819-99e3-7ea83f7bb498" />
---

## 🛠️ Tech Stack

* Python 3.x
* FastAPI
* Uvicorn
* Pandas
* PyPDF
* OpenPyXL
* HTML UI (local web interface)

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/saprecar/CAS_to_Spreadsheet.git
cd CAS_to_Spreadsheet
```

### 2. Install Python

Download Python from:
[https://www.python.org/](https://www.python.org/)

Make sure **pip** is installed (comes by default with Python).

---

### 3. Install dependencies

You can install manually:

```bash
pip install fastapi>=0.110.0
pip install uvicorn>=0.28.0
pip install python-multipart>=0.0.9
pip install pypdf>=4.0.0
pip install pandas>=2.2.0
pip install openpyxl>=3.1.2
```

OR simply run:

```bash
install_requirements.bat
```

---

## ▶️ How to Run

### Option 1 (Recommended)

Run the batch file:

```bash
run.bat
```

### Option 2 (Manual)

```bash
python main.py
```

---

## 🌐 Open Application

After starting the server, open your browser:

```
http://127.0.0.1:8000/
```

This will launch the local UI (no internet required after setup).

---

## 📂 Supported CAS Types

* CAMS CAS Statements

  * Summary
  * Detailed

* KFintech CAS Statements

  * Summary
  * Detailed

---

## ⚙️ Requirements

* Python 3.8+
* pip (Python package manager)
* Internet required only for initial dependency installation

---

## 📌 Notes

* Fully offline after installation
* Runs locally on your system
* Designed for ease of use for non-technical users
* You can verify batch scripts (`install_requirements.bat`, `run.bat`) using Notepad

---

## 📜 License

This project is free for personal and educational use.
Commercial use requires prior permission from the author.

---








