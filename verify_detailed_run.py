from parser import parse_cas_pdf
from exporter import generate_excel
import os

def run_verification():
    pdf_path = r"D:\VS code\Cas Parsar\Testing file\test file 2.pdf"
    password = "Incometax@123"
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return
        
    print(f"Reading {pdf_path}...")
    with open(pdf_path, 'rb') as f:
        file_bytes = f.read()
        
    print("Parsing PDF as DETAILED statement...")
    try:
        parsed_data = parse_cas_pdf(file_bytes, password, statement_type="detailed")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error parsing PDF: {e}")
        return
        
    holdings = parsed_data.get("holdings", [])
    metadata = parsed_data.get("metadata", {})
    
    print("\n--- METADATA ---")
    for k, v in metadata.items():
        print(f"{k}: {v}")
        
    print(f"\n--- HOLDINGS (Total: {len(holdings)}) ---")
    total_market = 0
    total_cost = 0
    total_txs = 0
    for h in holdings:
        total_market += h["market_value"]
        total_cost += h["cost_value"]
        total_txs += len(h["transactions"])
        
    print(f"Calculated Total Market Value: Rs. {total_market:,.2f}")
    print(f"Calculated Total Cost Value:   Rs. {total_cost:,.2f}")
    print(f"Total Transactions Extracted:  {total_txs}")
    
    print("\nGenerating Excel report...")
    excel_bytes = generate_excel(parsed_data)
    with open("test_detailed_report.xlsx", "wb") as f:
        f.write(excel_bytes.read())
    print("Saved as test_detailed_report.xlsx")
    
if __name__ == "__main__":
    run_verification()
