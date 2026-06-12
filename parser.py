import io
import re
import pypdf

def find_best_split(block, amount):
    """
    Intelligently splits a concatenated numeric string (e.g. '81.24946.154') 
    into Price and Units by testing all split points to see if Price * Units ~ Amount.
    """
    target_prod = abs(amount)
    block = block.strip()
    best_price = None
    best_units = None
    min_diff = float('inf')
    
    for i in range(1, len(block)):
        part1 = block[:i].strip()
        part2 = block[i:].strip()
        
        try:
            p_val = float(part1.replace(',', ''))
        except ValueError:
            continue
            
        try:
            u_str = part2.replace(',', '')
            if u_str.startswith('(') and u_str.endswith(')'):
                u_val = -float(u_str[1:-1])
            else:
                u_val = float(u_str)
        except ValueError:
            continue
            
        diff = abs(p_val * abs(u_val) - target_prod)
        if diff < min_diff:
            min_diff = diff
            best_price = p_val
            best_units = u_val
            
    if min_diff < 5.0:
        return best_price, best_units
    return None, None

def extract_metadata(text_lines):
    metadata = {
        "investor_name": "Unknown",
        "email": "Unknown",
        "mobile": "Unknown",
        "address": "Unknown",
        "statement_date": "Unknown"
    }
    
    address_lines = []
    collecting_address = False
    
    for i, line in enumerate(text_lines[:50]):
        line_clean = line.strip()
        if "As on " in line_clean:
            metadata["statement_date"] = line_clean.split("As on ")[-1].strip()
        elif "Email Id:" in line_clean:
            metadata["email"] = line_clean.split("Email Id:")[-1].strip()
            if i + 1 < len(text_lines):
                metadata["investor_name"] = text_lines[i+1].strip()
                collecting_address = True
        elif "Mobile:" in line_clean:
            metadata["mobile"] = line_clean.split("Mobile:")[-1].strip()
            collecting_address = False
            metadata["address"] = ", ".join(address_lines)
        elif collecting_address and i + 1 < len(text_lines):
            if text_lines[i].strip() != metadata["investor_name"]:
                address_lines.append(text_lines[i].strip())
    
    return metadata

def parse_summary_cas(text_lines, metadata):
    start_pattern = re.compile(r'^(\d+(?:/\d+)?)\s+([\d,]+\.\d{2})([A-Z0-9\s]+?)\s*-\s*(.*)')
    details_pattern = re.compile(r'^\s*([\d,]+\.\d{3})\s+(\d{1,2}-[A-Za-z]{3}-\d{4})\s+([\d,]+\.\d+)\s+(CAMS|KFINTECH|[A-Z]+)(INF[A-Z0-9]{9})\s+([\d,]+\.\d{3})')
    
    holdings = []
    current_holding = None
    
    for line in text_lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        start_match = start_pattern.match(line_clean)
        if start_match:
            folio, market_val, scheme_code, scheme_name_start = start_match.groups()
            current_holding = {
                "folio": folio,
                "market_value": float(market_val.replace(',', '')),
                "scheme_code": scheme_code.strip(),
                "scheme_name": scheme_name_start.strip(),
            }
            continue
            
        details_match = details_pattern.match(line_clean)
        if details_match:
            if current_holding:
                units, nav_date, nav, registrar, isin, cost_val = details_match.groups()
                current_holding.update({
                    "units": float(units.replace(',', '')),
                    "nav_date": nav_date,
                    "nav": float(nav.replace(',', '')),
                    "registrar": registrar,
                    "isin": isin,
                    "cost_value": float(cost_val.replace(',', ''))
                })
                scheme_upper = current_holding["scheme_name"].upper()
                if "NON DEMAT" in scheme_upper or "NON-DEMAT" in scheme_upper:
                    current_holding["demat_status"] = "Non-Demat"
                elif "DEMAT" in scheme_upper:
                    current_holding["demat_status"] = "Demat"
                else:
                    current_holding["demat_status"] = "Unknown"
                    
                gain = current_holding["market_value"] - current_holding["cost_value"]
                current_holding["absolute_gain"] = gain
                if current_holding["cost_value"] > 0:
                    current_holding["gain_percent"] = (gain / current_holding["cost_value"]) * 100
                else:
                    current_holding["gain_percent"] = 0.0

                current_holding["scheme_name"] = re.sub(r'\s+', ' ', current_holding["scheme_name"])
                holdings.append(current_holding)
                current_holding = None
            continue
            
        if current_holding:
            if "Page" in line_clean or "As on" in line_clean or "Consolidated" in line_clean or "CAMSCAS" in line_clean:
                continue
            current_holding["scheme_name"] += " " + line_clean

    return {"metadata": metadata, "holdings": holdings}


def parse_detailed_cas(text_lines, metadata):
    date_pattern = re.compile(r'^(\d{2}-[A-Za-z]{3}-\d{4})\s+(.*)')
    amount_pattern = re.compile(r'^(\([\d,]+\.\d{2}\)|-?[\d,]+\.\d{2})\s*(.*)')
    price_units_block_pattern = re.compile(r'^([\d,\.\(\)]+)\s*(.*)')
    balance_pattern = re.compile(r'\s+([\d,]+\.\d{3})\s*$')
    mf_pattern = re.compile(r'^([A-Z\s]+Mutual Fund|[A-Z\s]+MF|[A-Z\s]+Mutual\s+Fund.*)$', re.IGNORECASE)

    holdings = []
    current_holding = None
    current_mutual_fund = "Unknown"

    i = 0
    while i < len(text_lines):
        line = text_lines[i]
        line_clean = line.strip()
        if not line_clean:
            i += 1
            continue
        
        if mf_pattern.match(line_clean) and not "Page" in line_clean and not "As on" in line_clean:
            if len(line_clean) < 50:
                current_mutual_fund = line_clean.strip()
                
        if "ISIN:" in line_clean and not "Closing Unit" in line_clean:
            header_lines = []
            j = i
            while j < len(text_lines) and "Folio No:" not in text_lines[j]:
                header_lines.append(text_lines[j].strip())
                j += 1
            if j < len(text_lines):
                header_lines.append(text_lines[j].strip())
                
            header_text = " ".join(header_lines)
            
            isin_match = re.search(r'ISIN\s*:\s*([A-Z0-9]+)', header_text)
            isin = isin_match.group(1) if isin_match else "Unknown"
            
            registrar_match = re.search(r'Registrar\s*:\s*(\w+)', header_text)
            registrar = registrar_match.group(1) if registrar_match else "Unknown"
            if registrar == "Unknown":
                if "CAMS" in header_text:
                    registrar = "CAMS"
                elif "KFINTECH" in header_text:
                    registrar = "KFINTECH"
                    
            folio_match = re.search(r'Folio No\s*:\s*([\w\s\/]+)', header_text)
            folio = folio_match.group(1).strip() if folio_match else "Unknown"
            
            first_line = header_lines[0]
            code_name_match = re.match(r'^\s*([A-Za-z0-9]+)\s*-\s*(.*?)\s*-\s*ISIN:', first_line)
            if code_name_match:
                scheme_code = code_name_match.group(1).strip()
                scheme_name = code_name_match.group(2).strip()
            else:
                scheme_code = "Unknown"
                scheme_name = first_line.split(" - ISIN:")[0].strip()
                
            current_holding = {
                "mutual_fund": current_mutual_fund,
                "scheme_code": scheme_code,
                "scheme_name": scheme_name,
                "isin": isin,
                "registrar": registrar,
                "folio": folio,
                "transactions": [],
                "closing_balance": 0.0,
                "cost_value": 0.0,
                "market_value": 0.0,
                "nav": 0.0,
                "nav_date": "Unknown"
            }
            i = j
            
        elif current_holding is not None:
            if "NAV on" in line_clean and "Market Value on" in line_clean:
                nav_date_match = re.search(r'NAV on\s*([0-9a-zA-Z\-]+)\s*:', line_clean)
                nav_match = re.search(r'INR\s*([\d,]+\.\d+)', line_clean)
                mv_match = re.search(r'Market Value on.*INR\s*([\d,]+\.\d+)', line_clean)
                
                if nav_date_match:
                    current_holding["nav_date"] = nav_date_match.group(1)
                if nav_match:
                    current_holding["nav"] = float(nav_match.group(1).replace(',', ''))
                if mv_match:
                    current_holding["market_value"] = float(mv_match.group(1).replace(',', ''))
                    
            elif "Closing Unit Balance:" in line_clean and "Total Cost Value:" in line_clean:
                cub_match = re.search(r'Closing Unit Balance:\s*([\d,]+\.\d+)', line_clean)
                tcv_match = re.search(r'Total Cost Value:\s*([\d,]+\.\d+)', line_clean)
                
                if cub_match:
                    current_holding["closing_balance"] = float(cub_match.group(1).replace(',', ''))
                if tcv_match:
                    current_holding["cost_value"] = float(tcv_match.group(1).replace(',', ''))
                    
                gain = current_holding["market_value"] - current_holding["cost_value"]
                current_holding["absolute_gain"] = gain
                if current_holding["cost_value"] > 0:
                    current_holding["gain_percent"] = (gain / current_holding["cost_value"]) * 100
                else:
                    current_holding["gain_percent"] = 0.0
                    
                scheme_upper = current_holding["scheme_name"].upper()
                if "NON DEMAT" in scheme_upper or "NON-DEMAT" in scheme_upper:
                    current_holding["demat_status"] = "Non-Demat"
                elif "DEMAT" in scheme_upper:
                    current_holding["demat_status"] = "Demat"
                else:
                    current_holding["demat_status"] = "Unknown"
                    
                current_holding["units"] = current_holding["closing_balance"]
                    
                holdings.append(current_holding)
                current_holding = None
                
            else:
                date_match = date_pattern.match(line_clean)
                if date_match:
                    date_str, rest = date_match.groups()
                    amount_match = amount_pattern.match(rest)
                    if amount_match:
                        amount_str, rest = amount_match.groups()
                        amount = float(amount_str.replace('(', '-').replace(')', '').replace(',', ''))
                        
                        if rest and (rest[0].isdigit() or rest[0] == '('):
                            price_units_match = price_units_block_pattern.match(rest)
                            if price_units_match:
                                block_str, rest_after = price_units_match.groups()
                                price, units = find_best_split(block_str, amount)
                                
                                bal_match = balance_pattern.search(rest_after)
                                if bal_match:
                                    balance = float(bal_match.group(1).replace(',', ''))
                                    desc = rest_after[:bal_match.start()].strip()
                                    tx = {
                                        "date": date_str,
                                        "amount": amount,
                                        "price": price,
                                        "units": units,
                                        "desc": desc,
                                        "balance": balance
                                    }
                                    current_holding["transactions"].append(tx)
                                else:
                                    current_tx = {
                                        "date": date_str,
                                        "amount": amount,
                                        "price": price,
                                        "units": units,
                                        "desc": rest_after.strip(),
                                        "balance": None
                                    }
                                    k = i + 1
                                    while k < len(text_lines):
                                        next_line = text_lines[k].strip()
                                        if not next_line:
                                            k += 1
                                            continue
                                        if "Page" in next_line or "As on" in next_line or "Consolidated" in next_line or "CAMSCAS" in next_line:
                                            k += 1
                                            continue
                                        
                                        if re.match(r'^[\d,]+\.\d{3}$', next_line):
                                            current_tx["balance"] = float(next_line.replace(',', ''))
                                            k += 1
                                            break
                                        bal_match2 = balance_pattern.search(next_line)
                                        if bal_match2:
                                            current_tx["balance"] = float(bal_match2.group(1).replace(',', ''))
                                            current_tx["desc"] += " " + next_line[:bal_match2.start()].strip()
                                            k += 1
                                            break
                                        else:
                                            current_tx["desc"] += " " + next_line
                                            k += 1
                                            
                                    current_holding["transactions"].append(current_tx)
                                    i = k - 1
                            else:
                                tx = {
                                    "date": date_str,
                                    "amount": amount,
                                    "price": None,
                                    "units": None,
                                    "desc": rest.strip(),
                                    "balance": None
                                }
                                current_holding["transactions"].append(tx)
                        else:
                            bal_match = balance_pattern.search(rest)
                            if bal_match:
                                balance = float(bal_match.group(1).replace(',', ''))
                                desc = rest[:bal_match.start()].strip()
                            else:
                                balance = None
                                desc = rest.strip()
                            tx = {
                                "date": date_str,
                                "amount": amount,
                                "price": None,
                                "units": None,
                                "desc": desc,
                                "balance": balance
                            }
                            current_holding["transactions"].append(tx)
                            
        i += 1

    return {"metadata": metadata, "holdings": holdings}


def parse_cas_pdf(file_bytes, password, statement_type="summary"):
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    if reader.is_encrypted:
        success = reader.decrypt(password)
        if not success:
            raise ValueError("Incorrect password or failed to decrypt.")
            
    text_lines = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_lines.extend(page_text.split('\n'))

    metadata = extract_metadata(text_lines)
    
    if statement_type == "detailed":
        return parse_detailed_cas(text_lines, metadata)
    else:
        return parse_summary_cas(text_lines, metadata)
