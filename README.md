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
git clone https://github.com/your-username/CAS_to_Spreadsheet.git
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

