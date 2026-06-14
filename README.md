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
* packaging
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
pip install packaging>=24.0
```

OR simply run:

```bash
install_requirements.bat
```

---

## ▶️ How to Run

### Option 1 (Recommended)

Run the launcher script for your operating system:

| Operating System | Script |
|------------------|--------|
| Windows | `run.bat` |
| Linux | `run.sh` |
| macOS | `run.command` |

---

### Option 2 (Manual)

Run the application directly with Python:

```bash
python main.py
```

> **Note:** On some systems, you may need to use:
>
> ```bash
> python3 main.py
> ```

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

## ⚠️ Disclaimer
* This software is provided for educational and personal use only
* It is not intended for production, financial decision-making, or official reporting use
* It does not provide any financial, legal, tax, medical, or professional advice
* It does not provide tips, recommendations, suggestions, opinions, interpretations, or analysis of any kind
* All outputs are purely mechanical results of user-provided data processing and extraction
* The developer does not endorse or guarantee any decision made based on the output
## 🔐 Data Privacy & Security
* All data processing is performed locally on the user’s system by default
* The software does not collect, store, or transmit any user data externally
* Internet access is used only if explicitly enabled by the user
* If the user enables external connectivity (APIs, libraries, or scripts), any resulting data exposure is solely the user’s responsibility
* The developer is not responsible for data leakage, unauthorized access, or security vulnerabilities caused by user actions or system configuration
## 📊 Accuracy & Output Limitations
* The software may produce incomplete, partial, or incorrect extraction results
* Formatting issues, parsing errors, or missing fields may occur depending on input file structure
* No guarantee is provided regarding:
  * Accuracy of extracted data
  * Completeness of results
  * Compatibility with all file formats or versions
  * Suitability for legal, financial, or official use
  * Users must independently verify all outputs before relying on them
## 👤 User Responsibility
* Users are solely responsible for:
* Validity and safety of input files and data
* Reviewing and verifying all outputs
* Ensuring lawful use of the software
* Preventing misuse, modification, or malicious execution
* Any consequences arising from misuse are entirely the user’s responsibility
* Users are expected to have basic understanding of how to safely run Python-based applications
## ⚙️ System Behavior
* The software runs locally on the user’s machine
* It may depend on external Python libraries installed via pip
* It is designed for offline-first usage after setup
* Performance and results may vary depending on system configuration and input data quality
## 🚫 Limitations of Use
* This software must not be used for:
  * Financial advisory or investment decisions
  * Legal or regulatory submissions without verification
  * Automated decision-making in critical systems
* It is strictly a data processing and extraction utility, not an analytical or advisory tool
## ™️ Intellectual Property
* All product names, logos, trademarks, and other intellectual property referenced in this project are the property of their respective owners
* Any third-party names or brands are used for identification and reference purposes only
* No ownership, endorsement, or affiliation is implied or claimed by the developer
* This project does not intend to infringe on any copyright, trademark, or intellectual property rights
* Email for Removal of tool








