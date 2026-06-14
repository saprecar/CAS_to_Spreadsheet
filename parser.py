import io
import re
import pypdf

def _safe_float(s):
    """Convert string to float, returning None for non-numeric tokens like '-'."""
    if s is None:
        return None
    cleaned = s.strip().replace('(', '-').replace(')', '').replace(',', '')
    # A valid number must contain at least one digit
    if not any(c.isdigit() for c in cleaned):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None

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

def detect_provider(text_lines):
    text = "\n".join(text_lines[:150]).upper()
    if "CAMSCASWS" in text:
        return "CAMS"
    if "KFINCAS" in text:
        return "KFIN"
    if "INITIATIVE BY KFIN AND CAMS" in text:
        return "KFIN"
    if "INITIATIVE BY CAMS AND KFINTECH" in text:
        return "CAMS"
        
    for line in text_lines[:100]:
        line_upper = line.upper()
        if "KFINTECH" in line_upper or "KFIN" in line_upper or "KFINCAS" in line_upper:
            return "KFIN"
    return "CAMS"

def is_candidate_name(line):
    line_clean = line.strip()
    if not (3 <= len(line_clean) <= 45):
        return False
    if re.search(r'\d', line_clean):
        return False
    lower_line = line_clean.lower()
    keywords = [
        "mobile", "email", "pan", "folio", "consolidated", "friendly", "brought", "page", "active", "load",
        "colony", "street", "road", "nagar", "floor", "house", "flat", "building", "sector", "block", "india",
        "state", "district", "city", "town", "post", "via", "near", "opposite", "behind", "beside", "disclaimer",
        "attention", "note", "as on", "valuation", "cost", "market", "mutual", "fund", "registrar", "nominee", "kyc",
        "inr", "holding", "pradesh", "bengal", "karnataka", "maharashtra", "gujarat", "kerala", "tamil", "nadu", 
        "andhra", "telangana", "bihar", "punjab", "haryana", "rajasthan", "delhi", "kashmir", "assam", "odisha"
    ]
    if any(k in lower_line for k in keywords):
        return False
    return True

def extract_metadata(text_lines):
    metadata = {
        "investor_name": "Unknown",
        "pan": "Unknown",
        "email": "Unknown",
        "mobile": "Unknown",
        "address": "Unknown",
        "statement_date": "Unknown"
    }
    
    address_lines = []
    collecting_address = False
    
    for i, line in enumerate(text_lines[:150]):
        line_clean = line.strip()
        line_lower = line_clean.lower()
        
        as_on_match = re.search(r'as\s+on\s+(\d{1,2}-[A-Za-z]{3}-\d{4})', line_clean, re.IGNORECASE)
        if as_on_match:
            metadata["statement_date"] = as_on_match.group(1)
        else:
            to_date_match = re.search(r'to\s+(\d{1,2}-[A-Za-z]{3}-\d{4})', line_clean, re.IGNORECASE)
            if to_date_match:
                metadata["statement_date"] = to_date_match.group(1)
        
        if "email" in line_lower and ":" in line_clean:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line_clean)
            if email_match:
                metadata["email"] = email_match.group(0)
                if metadata["investor_name"] == "Unknown":
                    if i + 1 < len(text_lines):
                        next_line = text_lines[i+1].strip()
                        if is_candidate_name(next_line):
                            metadata["investor_name"] = next_line
                            collecting_address = True
                            
                if metadata["investor_name"] == "Unknown":
                    for name_idx in range(max(0, i - 10), i):
                        cand = text_lines[name_idx].strip()
                        if is_candidate_name(cand):
                            metadata["investor_name"] = cand
                            break
        
        elif "mobile" in line_lower and ":" in line_clean:
            parts = re.split(r'mobile\s*:\s*', line_clean, flags=re.IGNORECASE)
            if len(parts) > 1:
                metadata["mobile"] = parts[1].split()[0].strip()
            collecting_address = False
            if address_lines:
                metadata["address"] = ", ".join(address_lines)
                
        elif collecting_address:
            if any(k in line_lower for k in ["mobile", "email", "pan", "folio", "closing unit", "valuation"]):
                collecting_address = False
                if address_lines:
                    metadata["address"] = ", ".join(address_lines)
            else:
                if line_clean and line_clean != metadata["investor_name"]:
                    address_lines.append(line_clean)
                    
    if metadata["investor_name"] == "Unknown":
        for line in text_lines[:40]:
            if is_candidate_name(line):
                metadata["investor_name"] = line.strip()
                break
                
    if metadata["address"] == "Unknown" and address_lines:
        metadata["address"] = ", ".join(address_lines)

    # Extract PAN — format: 5 uppercase letters, 4 digits, 1 uppercase letter
    # KFin sometimes runs PAN directly into next word: "PAN: ABCDE1234FFolio"
    if metadata["pan"] == "Unknown":
        pan_value_re = re.compile(r'PAN\s*:?\s*([A-Z]{5}[0-9]{4}[A-Z])', re.IGNORECASE)
        for line in text_lines[:500]:
            pm = pan_value_re.search(line)
            if pm:
                metadata["pan"] = pm.group(1).upper()
                break
        # Fallback: bare PAN anywhere (word boundary before, not needed after)
        if metadata["pan"] == "Unknown":
            bare_pan_re = re.compile(r'\b([A-Z]{5}[0-9]{4}[A-Z])')
            for line in text_lines[:500]:
                bm = bare_pan_re.search(line)
                if bm:
                    metadata["pan"] = bm.group(1).upper()
                    break

        
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

def parse_kfin_summary(text_lines, metadata):
    start_pattern = re.compile(r'^(CAMS|KFINTECH)(\d+)\s+([A-Z0-9]+)-(.*)', re.IGNORECASE)
    details_pattern = re.compile(
        r'^\s*([\d,.-]+)\s+(\d{1,2}-[A-Za-z]{3}-\d{4})\s+([\d,.-]+)\s+([\d,.-]+)(INF[A-Z0-9]{9})\s+([\d,.-]+)'
    )
    
    holdings = []
    current_holding = None
    
    for line in text_lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        start_match = start_pattern.match(line_clean)
        if start_match:
            registrar, folio, scheme_code, scheme_name_start = start_match.groups()
            current_holding = {
                "folio": folio,
                "scheme_code": scheme_code.strip(),
                "scheme_name": scheme_name_start.strip(),
                "registrar": registrar.upper()
            }
            continue
            
        details_match = details_pattern.match(line_clean)
        if details_match:
            if current_holding:
                units, nav_date, nav, market_val, isin, cost_val = details_match.groups()
                current_holding.update({
                    "units": float(units.replace(',', '')),
                    "nav_date": nav_date,
                    "nav": float(nav.replace(',', '')),
                    "market_value": float(market_val.replace(',', '')),
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
            if "Page" in line_clean or "As on" in line_clean or "Consolidated" in line_clean or "CAMSCAS" in line_clean or "KFINCAS" in line_clean:
                continue
            current_holding["scheme_name"] += " " + line_clean
            
    return {"metadata": metadata, "holdings": holdings}

def parse_detailed_cas(text_lines, metadata):
    date_pattern = re.compile(r'^(\d{2}-[A-Za-z]{3}-\d{4})(?:(?:\d{2}-[A-Za-z]{3}-\d{4})+)?\s*(.*)')
    # Amount must start with '(' or digit; units/price/balance must contain digits
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
                    
            if "Closing Unit Balance:" in line_clean and "Total Cost Value:" in line_clean:
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

def parse_kfin_detailed(text_lines, metadata):
    holdings = []
    current_holding = None
    current_mutual_fund = "Unknown"
    current_tx = None
    
    mf_pattern = re.compile(r'^([A-Z\s]+Mutual Fund|[A-Z\s]+MF|[A-Z\s]+Mutual\s+Fund.*)$', re.IGNORECASE)
    date_pattern = re.compile(r'^(\d{2}-[A-Za-z]{3}-\d{4})(?:(?:\d{2}-[A-Za-z]{3}-\d{4})+)?\s*(.*)')
    
    # Require at least one digit in each numeric group to avoid matching bare '-'
    four_nums_pattern = re.compile(
        r'(?:^|\s+)(\([\d][\d,.-]*\)|-?[\d][\d,.-]*)\s+(\([\d][\d,.-]*\)|-?[\d][\d,.-]*)\s+([\d][\d,.-]*)\s+([\d][\d,.-]*)$'
    )
    one_num_pattern = re.compile(
        r'(?:^|\s+)(\([\d][\d,.-]*\)|-?[\d][\d,.-]*)$'
    )

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
            if current_tx and current_holding:
                current_holding["transactions"].append(current_tx)
                current_tx = None
                
            header_lines = []
            
            # Find Folio No by searching upwards
            folio = "Unknown"
            up = i
            while up >= max(0, i - 10):
                if "Folio No" in text_lines[up]:
                    folio_match = re.search(r'Folio No\s*:\s*([\d\s\/-]+)', text_lines[up])
                    if folio_match:
                        folio = folio_match.group(1).strip()
                    break
                up -= 1
                
            # Collect header lines downwards until Opening Unit
            j = i
            while j < len(text_lines) and "Opening Unit" not in text_lines[j] and "Opening Balance" not in text_lines[j]:
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
                elif "KFIN" in header_text:
                    registrar = "KFINTECH"
                    
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
            i += 1
            continue
            
        elif current_holding is not None and "Closing Unit Balance:" in line_clean:
            if current_tx:
                current_holding["transactions"].append(current_tx)
                current_tx = None
                
            tcv_match = re.search(r'Total Cost Value\s*:\s*(?:INR\s*)?([\d,]+\.\d+)', line_clean)
            nav_date_match = re.search(r'NAV on\s*([0-9a-zA-Z\-]+)', line_clean)
            nav_match = re.search(r'NAV on\s*[0-9a-zA-Z\-]+\s*:\s*(?:INR\s*)?([\d,]+\.\d+)', line_clean)
            cub_match = re.search(r'Closing Unit Balance\s*:\s*(-?[\d,.]+)(?:\s|$|\d{2}-[A-Za-z]{3})', line_clean)
            if cub_match:
                val_str = cub_match.group(1).rstrip('.')
                current_holding["closing_balance"] = _safe_float(val_str)
            if tcv_match:
                current_holding["cost_value"] = float(tcv_match.group(1).replace(',', ''))
            if nav_date_match:
                current_holding["nav_date"] = nav_date_match.group(1)
            if nav_match:
                current_holding["nav"] = float(nav_match.group(1).replace(',', ''))
            mv_match = re.search(r'Market Value on.*?(?:INR\s*)?([\d,]+\.\d+)', line_clean)
            
            if mv_match:
                current_holding["market_value"] = float(mv_match.group(1).replace(',', ''))
                
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
            
        elif current_holding is not None:
            if "Page" in line_clean or "As on" in line_clean or "Consolidated" in line_clean or "KFINCAS" in line_clean:
                i += 1
                continue
                
            date_match = date_pattern.match(line_clean)
            if date_match:
                if current_tx:
                    current_holding["transactions"].append(current_tx)
                    current_tx = None
                    
                date_str, rest = date_match.groups()
                
                while True:
                    rest_clean = rest.strip()
                    second_date_match = date_pattern.match(rest_clean)
                    if second_date_match:
                        date_str, rest = second_date_match.groups()
                    else:
                        break
                
                four_nums_match = four_nums_pattern.search(rest)
                if four_nums_match:
                    amount_str, units_str, price_str, balance_str = four_nums_match.groups()
                    desc = rest[:four_nums_match.start()].strip()
                    
                    amount  = _safe_float(amount_str)
                    units   = _safe_float(units_str)
                    price   = _safe_float(price_str)
                    balance = _safe_float(balance_str)
                    
                    current_tx = {
                        "date": date_str,
                        "amount": amount,
                        "price": price,
                        "units": units,
                        "desc": desc,
                        "balance": balance
                    }
                else:
                    one_num_match = one_num_pattern.search(rest)
                    if one_num_match:
                        amount_str = one_num_match.group(1)
                        desc = rest[:one_num_match.start()].strip()
                        amount = _safe_float(amount_str)
                        
                        current_tx = {
                            "date": date_str,
                            "amount": amount,
                            "price": None,
                            "units": None,
                            "desc": desc,
                            "balance": None
                        }
                    else:
                        # Non-financial annotation entry (e.g. nominee change, email update)
                        # Treat trailing '-' as no amount
                        desc = rest.strip()
                        if desc.endswith(' -'):
                            desc = desc[:-2].strip()
                        current_tx = {
                            "date": date_str,
                            "amount": None,
                            "price": None,
                            "units": None,
                            "desc": desc,
                            "balance": None
                        }
            else:
                if current_tx is not None:
                    # Check if numbers were wrapped to the next line
                    if current_tx.get("amount") is None:
                        four_match = four_nums_pattern.search(line_clean)
                        if four_match:
                            a, u, p, b = four_match.groups()
                            current_tx["amount"] = _safe_float(a)
                            current_tx["units"] = _safe_float(u)
                            current_tx["price"] = _safe_float(p)
                            current_tx["balance"] = _safe_float(b)
                            rem_desc = line_clean[:four_match.start()].strip()
                            if rem_desc:
                                current_tx["desc"] += " " + rem_desc
                            i += 1
                            continue
                            
                        one_match = one_num_pattern.search(line_clean)
                        if one_match:
                            b = one_match.group(1)
                            current_tx["balance"] = _safe_float(b)
                            rem_desc = line_clean[:one_match.start()].strip()
                            if rem_desc:
                                current_tx["desc"] += " " + rem_desc
                            i += 1
                            continue
                    
                    current_tx["desc"] += " " + line_clean
                    
        i += 1
        
    if current_tx and current_holding:
        current_holding["transactions"].append(current_tx)

    return {"metadata": metadata, "holdings": holdings}

def _extract_text_lines(file_bytes, password):
    """
    Extract text from a (possibly encrypted) PDF using pypdf layout mode.
    This preserves the visual layout of the PDF and prevents page-level 
    reflows that cause transactions to appear before their headers.
    """
    raw_lines = []
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        if reader.is_encrypted:
            if not reader.decrypt(password):
                raise ValueError("Incorrect password or failed to decrypt.")
                
        for page in reader.pages:
            t = page.extract_text(extraction_mode="layout")
            if t:
                raw_lines.extend(t.split('\n'))
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {str(e)}")
    return raw_lines


def parse_cas_pdf(file_bytes, password, statement_type="summary", provider="AUTO"):
    text_lines = _extract_text_lines(file_bytes, password)

    base_metadata = {
        "statement_period": "",
        "email": "",
        "statement_type": statement_type
    }
    extracted_meta = extract_metadata(text_lines)
    base_metadata.update(extracted_meta)
    metadata = base_metadata

    if provider == "AUTO":
        provider = detect_provider(text_lines)

    if statement_type == "detailed":
        if provider == "CAMS":
            return parse_detailed_cas(text_lines, metadata)
        else:
            return parse_kfin_detailed(text_lines, metadata)
    else:
        if provider == "CAMS":
            return parse_summary_cas(text_lines, metadata)
        else:
            return parse_kfin_summary(text_lines, metadata)
