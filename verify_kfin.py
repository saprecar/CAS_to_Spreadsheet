from parser import parse_cas_pdf
from exporter import generate_excel
import os

def test_kfin():
    password = "YOUR_PASSWORD_HERE"
    
    # 1. Test Summary Statement
    summary_pdf_path = r"D:\VS code\Cas Parsar\test file\Kfintech statement summary.pdf"
    if os.path.exists(summary_pdf_path):
        print(f"\n--- Testing KFintech Summary Statement: {summary_pdf_path} ---")
        with open(summary_pdf_path, 'rb') as f:
            file_bytes = f.read()
        
        parsed_data = parse_cas_pdf(file_bytes, password, statement_type="summary")
        holdings = parsed_data.get("holdings", [])
        metadata = parsed_data.get("metadata", {})
        
        print(f"Investor Name: {metadata.get('investor_name')}")
        print(f"Email: {metadata.get('email')}")
        print(f"Mobile: {metadata.get('mobile')}")
        print(f"Statement Date: {metadata.get('statement_date')}")
        print(f"Total Holdings parsed: {len(holdings)}")
        
        # Save Excel
        excel_bytes = generate_excel(parsed_data)
        with open("verify_kfin_summary.xlsx", "wb") as f:
            f.write(excel_bytes.read())
        print("Generated verify_kfin_summary.xlsx successfully.")
    else:
        print(f"Error: {summary_pdf_path} not found.")

    # 2. Test Detailed Statement
    detailed_pdf_path = r"D:\VS code\Cas Parsar\test file\Kfintech statement details.pdf"
    if os.path.exists(detailed_pdf_path):
        print(f"\n--- Testing KFintech Detailed Statement: {detailed_pdf_path} ---")
        with open(detailed_pdf_path, 'rb') as f:
            file_bytes = f.read()
            
        parsed_data = parse_cas_pdf(file_bytes, password, statement_type="detailed")
        holdings = parsed_data.get("holdings", [])
        metadata = parsed_data.get("metadata", {})
        
        print(f"Investor Name: {metadata.get('investor_name')}")
        print(f"Email: {metadata.get('email')}")
        print(f"Mobile: {metadata.get('mobile')}")
        print(f"Statement Date: {metadata.get('statement_date')}")
        print(f"Total Holdings parsed: {len(holdings)}")
        
        tx_count = sum(len(h.get("transactions", [])) for h in holdings)
        print(f"Total Transactions parsed: {tx_count}")
        
        # Save Excel
        excel_bytes = generate_excel(parsed_data)
        with open("verify_kfin_detailed.xlsx", "wb") as f:
            f.write(excel_bytes.read())
        print("Generated verify_kfin_detailed.xlsx successfully.")
    else:
        print(f"Error: {detailed_pdf_path} not found.")

if __name__ == "__main__":
    test_kfin()
