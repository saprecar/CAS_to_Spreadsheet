from parser import parse_cas_pdf
import os

def run_verification():
    pdf_path = r"D:\VS code\Cas Parsar\Testing file\Testing File.pdf"
    password = "YOUR_PASSWORD_HERE"
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return
        
    print(f"Reading {pdf_path}...")
    with open(pdf_path, 'rb') as f:
        file_bytes = f.read()
        
    print("Parsing PDF...")
    try:
        parsed_data = parse_cas_pdf(file_bytes, password)
    except Exception as e:
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
    for h in holdings:
        total_market += h["market_value"]
        total_cost += h["cost_value"]
        
    print(f"Calculated Total Market Value: Rs. {total_market:,.2f}")
    print(f"Calculated Total Cost Value:   Rs. {total_cost:,.2f}")
    
    expected_market = 484716.13
    expected_cost = 395572.45
    
    diff_market = abs(total_market - expected_market)
    diff_cost = abs(total_cost - expected_cost)
    
    print(f"\nDifference Market Value: {diff_market:.2f}")
    print(f"Difference Cost Value:   {diff_cost:.2f}")
    
    if diff_market <= 0.1 and diff_cost <= 0.1:
        print("\nSUCCESS: Calculated totals perfectly match the PDF summary!")
    else:
        print("\nWARNING: Totals do not match expected values.")

if __name__ == "__main__":
    run_verification()
