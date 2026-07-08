"""
PDF Analysis Utility for Intelligent Data Extraction
Analyzes vendor receipts and extracts structured data
"""

import re
from decimal import Decimal
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
    
    # Cross-platform Tesseract configuration
    import os
    from django.conf import settings
    if hasattr(settings, 'TESSERACT_CMD') and settings.TESSERACT_CMD and os.path.exists(settings.TESSERACT_CMD):
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
except ImportError:
    pass

try:
    import fitz  # PyMuPDF
except ImportError:
    pass


class PDFAnalyzer:
    """Intelligent PDF Receipt Analyzer"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text = ""
        self.extracted_data = {}
    
    def extract_text_from_pdf(self) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(self.pdf_path)
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text with PyMuPDF: {e}")
            return ""
    
    def extract_text_with_ocr(self) -> str:
        """Extract text from scanned PDF using Tesseract OCR"""
        try:
            images = convert_from_path(self.pdf_path)
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text with OCR: {e}")
            return ""
    
    def analyze(self) -> Dict[str, Any]:
        """Main analysis function - intelligently extracts all fields"""
        
        # Try text extraction first, then OCR if needed
        self.text = self.extract_text_from_pdf()
        if not self.text or len(self.text) < 10:
            self.text = self.extract_text_with_ocr()
        
        if not self.text:
            return {"error": "Could not extract text from PDF"}
        
        # Extract all possible fields
        self.extracted_data = {
            'vendor_name': self._extract_vendor_name(),
            'material_name': self._extract_material_name(),
            'quantity': self._extract_quantity(),
            'unit_price': self._extract_unit_price(),
            'total_cost': self._extract_total_cost(),
            'date_received': self._extract_date(),
            'ro_number': self._extract_ro_number(),
            'vendor_code': self._extract_vendor_code(),
            'hsn_code': self._extract_hsn_code(),
            'description': self._extract_description(),
            'gst': self._extract_gst(),
            'invoice_number': self._extract_invoice_number(),
            'consignee': self._extract_consignee(),
            'r_note_no': self._extract_r_note_no(),
            'po_at_no': self._extract_po_at_no(),
            'pl_no': self._extract_pl_no(),
        }
        
        # Auto-calculate unit_price if missing or 0
        try:
            qty = float(self.extracted_data.get('quantity') or 0)
            total = float(self.extracted_data.get('total_cost') or 0)
            price = float(self.extracted_data.get('unit_price') or 0)
            if qty > 0 and total > 0 and (price <= 0 or not self.extracted_data.get('unit_price')):
                self.extracted_data['unit_price'] = f"{total / qty:.2f}"
        except Exception:
            pass
        
        # Remove None values
        self.extracted_data = {k: v for k, v in self.extracted_data.items() if v is not None}
        
        return self.extracted_data
    
    def _extract_vendor_name(self) -> str:
        """Extract vendor/company name (no address)"""
        lines = [line.strip() for line in self.text.split('\n') if line.strip()]
        for i, line in enumerate(lines):
            if line.startswith("M/s ") or "M/s" in line:
                vendor = line
                # Look ahead up to 3 lines to grab wrapped name
                for j in range(1, 4):
                    if i + j < len(lines):
                        next_line = lines[i + j]
                        # Stop if we hit address components
                        if (any(addr in next_line.lower() for addr in ['sector', 'bawana', 'road', 'plot', 'h-', 'shop', 'near', 'street', 'delhi', 'floor', 'industrial', 'complex', 'block']) or 
                            re.match(r'^\d+', next_line) or 
                            ',' in next_line or 
                            'Vendor Code' in next_line):
                            break
                        vendor += " " + next_line
                return vendor.strip()
                
        # Fallback to regex
        patterns = [
            r'(?:Vendor|Company|From|Supplier|Billed by|Seller|Name & Address of Supplier)[\s:]*([^\n,]+)',
            r'[A-Z][A-Za-z\s&.,]+(?:Ltd|Limited|Inc|Corp|Company|Industries|Enterprises)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE | re.MULTILINE)
            if match:
                vendor = match.group(1).strip()
                if len(vendor) > 3 and len(vendor) < 200:
                    return vendor
        return None
    
    def _extract_material_details(self):
        """Intelligently parses layout blocks to isolate material details from metadata"""
        lines = [line.strip() for line in self.text.split('\n') if line.strip()]
        
        # Find start index
        start_idx = -1
        for i, line in enumerate(lines):
            if "description & drg" in line.lower():
                start_idx = i
                break
                
        if start_idx == -1:
            return None, None
            
        # Collect lines after start_idx until we hit an end marker
        collected_lines = []
        end_markers = [
            'date of', 'terms of', 'gate/challan', 'consignee', 
            'rn quantity', 'ro quantity', 'is-no', 'isl-no', 
            'freight', 'packing', 'forwarding'
        ]
        
        for line in lines[start_idx + 1:]:
            # Check if this line is an end marker
            if any(marker in line.lower() for marker in end_markers):
                break
            # Skip other metadata lines
            if any(k in line.lower() for k in ['pl no', 'value:', 'drr-no', 'isl-no', 'date:', 'dated']):
                continue
            # Skip code matches like R1260087 or R1260089
            if re.match(r'^R\d{6,8}$', line):
                continue
            collected_lines.append(line)
            
        if not collected_lines:
            return None, None
            
        # Split into name and description based on the presence of "(Detailed"
        name_lines = []
        desc_lines = []
        found_detailed = False
        
        for line in collected_lines:
            if found_detailed:
                desc_lines.append(line)
            else:
                # Check for various formats of detailed spec start
                match = re.search(r'\((?:detailed| detailed|Detailed|Detailed Description)', line)
                if match:
                    found_detailed = True
                    split_idx = match.start()
                    before = line[:split_idx].strip()
                    after = line[split_idx:].strip()
                    if before:
                        name_lines.append(before)
                    if after:
                        desc_lines.append(after)
                else:
                    name_lines.append(line)
                    
        name = " ".join(name_lines).strip()
        description = " ".join(desc_lines).strip()
        return name, description

    def _extract_material_name(self) -> str:
        """Extract material/product name"""
        name, _ = self._extract_material_details()
        if name:
            return name
            
        # Prioritize specific labels and filter out generic keywords like 'Details'
        patterns = [
            r'(?:Material\s+Name|Product\s+Name|Item\s+Name)[\s:]*([^\n]+)',
            r'(?:Material|Product)[\s:]*([^\n]+)',
            r'(?:Item|Description|Article)[\s:]*([^\n]+)',
            r'(?:^|\n)([A-Z][A-Za-z0-9\s]+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.MULTILINE | re.IGNORECASE)
            if match:
                material = match.group(1).strip()
                # Filter out generic table headers / columns
                if material.lower() in ['details', 'description', 'specifications', 'invoice', 'receipt', 'item details']:
                    continue
                if 5 < len(material) < 255 and not re.match(r'^\d+$', material):
                    return material
        return None
    
    def _extract_quantity(self) -> str:
        """Extract quantity"""
        patterns = [
            r'(?:Qty|Quantity|Units|Count)[\s:]*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:units?|pieces?|nos?|boxes?|packs?|kgs?|litres?|packets?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_unit_price(self) -> str:
        """Extract unit price"""
        patterns = [
            r'(?:Unit Price|Rate|Price per Unit|Unit Cost)[\s:]*Rs\.?\s*(\d+(?:\.\d+)?)',
            r'(?:Price|Rate)[\s:]*Rs\.?\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_total_cost(self) -> str:
        """Extract total cost"""
        patterns = [
            r'Value\s*:\s*(?:Rs\.)?\s*([\d\.]+)',
            r'(?:Total|Grand Total|Net Amount|Amount Due)[\s:]*Rs\.?\s*(\d+(?:\.\d+)?)',
            r'(?:Total|Amount)[\s:]*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_date(self) -> str:
        """Extract date received"""
        patterns = [
            r'(?:Date|Invoice Date|Bill Date)[\s:]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text)
            if match:
                date_str = match.group(1).strip()
                try:
                    # Try parsing different date formats
                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y', '%m/%d/%Y', '%m-%d-%Y']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            return parsed_date.strftime('%Y-%m-%d')
                        except ValueError:
                            continue
                except Exception:
                    pass
        return None
    
    def _extract_ro_number(self) -> str:
        """Extract RO Number from receipt"""
        # 1. Try same-line match without matching newlines in whitespace!
        patterns = [
            r'R\.?O\.?\s*(?:No|Number|No\.)\.?[^\S\r\n]*[:\-]?[^\S\r\n]*([A-Za-z0-9\-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                if val.lower() != 'r':
                    return val
                    
        # 2. Try signature block/WARD-R.O. match
        sig_match = re.search(r'WARD-R\.?O\.?\s*([A-Za-z0-9\-]+)', self.text, re.IGNORECASE)
        if sig_match:
            return sig_match.group(1).strip()
                
        # 3. Search for next-line match
        lines = [line.strip() for line in self.text.split('\n') if line.strip()]
        for i, line in enumerate(lines):
            if re.match(r'^R\.?O\.?\s*(?:No|Number)\.?\s*[:\-]?$', line.strip(), re.IGNORECASE):
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not any(lbl in next_line.lower() for lbl in ['date', 'consignee', 'qty']):
                        return next_line
        return None

    def _extract_vendor_code(self) -> str:
        """Extract Vendor Code from receipt"""
        # 1. Search for pattern "Vendor Code : <value>" or "Vendor Code <value>"
        match = re.search(r'Vendor\s+Code\s*[:\-]?\s*([A-Za-z0-9\-]+)', self.text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # 2. Look for "Vendor Code" line and take next line
        lines = [line.strip() for line in self.text.split('\n') if line.strip()]
        for i, line in enumerate(lines):
            if re.match(r'^vendor\s+code$', line.strip(), re.IGNORECASE):
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not any(lbl in next_line.lower() for lbl in ['depot', 'ward', 'r.o.no', 'date', 'r/note']):
                        return next_line
        return None
    
    def _extract_hsn_code(self) -> str:
        """Extract HSN code (for Indian goods)"""
        patterns = [
            r'(?:HSN|HSN Code|SAC)[\s:]*([0-9]{2,8})',
            r'\b([0-9]{8})\b(?=\s|$)',  # 8-digit HSN code
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                hsn = match.group(1).strip()
                if 4 <= len(hsn) <= 8:
                    return hsn
        return None
    
    def _extract_description(self) -> str:
        """Extract product description / Remarks / Inspection Report from the receipt"""
        lines = [line.strip() for line in self.text.split('\n') if line.strip()]
        
        # 1. Search for "Inspection Report"
        start_idx = -1
        for i, line in enumerate(lines):
            if "inspection report" in line.lower():
                start_idx = i
                break
                
        # 2. If not found, search for "Remarks"
        if start_idx == -1:
            for i, line in enumerate(lines):
                if line.lower().startswith("remarks:") or line.lower() == "remarks":
                    start_idx = i
                    break
                    
        if start_idx == -1:
            # Fallback to the original description extraction
            _, desc = self._extract_material_details()
            return desc or ""
            
        # Collect lines from start_idx until we hit an end marker
        collected = []
        end_markers = [
            'rr/mtr no', 'challan/invoice', 'due date', 'actual date',
            'qty.invoiced', 'qty.received', 'qty.accepted', 'depot officer',
            'despatching', 'receiving official', 'signature not verified',
            'block copy', 'original po details', 'e-dispatch note'
        ]
        
        first_line = lines[start_idx]
        collected.append(first_line)
            
        for line in lines[start_idx + 1:]:
            if any(marker in line.lower() for marker in end_markers):
                break
            collected.append(line)
            
        return "\n".join(collected).strip()
    
    def _extract_gst(self) -> str:
        """Extract GST amount"""
        patterns = [
            r'(?:GST|Tax|SGST|CGST)[\s:]*(?:Rs\.)?[\s]*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:%\s*)?(?:GST|Tax)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_invoice_number(self) -> str:
        """Extract invoice number"""
        # Prioritize exact names to avoid matching isolated slashes from page headers (e.g. 'INVOICE / RECEIPT')
        patterns = [
            r'(?:Invoice\s+No|Invoice\s+Number|Bill\s+No|Order\s+No|PO\s+Number)[\s:#]*([A-Za-z0-9\-]+)',
            r'(?:Invoice|Bill|PO|Order)[\s:#]+([A-Za-z0-9\-]{4,})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                inv_no = match.group(1).strip()
                if len(inv_no) < 50:
                    return inv_no
        return None

    def _extract_consignee(self) -> str:
        """Extract consignee name/depot"""
        lines = [line.strip() for line in self.text.split('\n') if line.strip()]
        for i, line in enumerate(lines):
            if line.lower() == "consignee":
                consignee_parts = []
                # Look ahead up to 5 lines to grab wrapped consignee
                for j in range(1, 6):
                    if i + j < len(lines):
                        next_line = lines[i + j]
                        if any(lbl in next_line.lower() for lbl in ['p.o.qty', 'bal.p.o.qty', 'qty.invoiced', 'qty.received', 'qty.accepted', 'original po']):
                            break
                        consignee_parts.append(next_line)
                return " ".join(consignee_parts).strip()
        # Fallback
        patterns = [
            r'Consignee\s*:\s*([^\n]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_r_note_no(self) -> str:
        """Extract R/Note No."""
        patterns = [
            r'R/Note-No\.\n\s*([\w\d]+)',
            r'R/Note-No\.\s*([\w\d]+)',
            r'R/Note\s*No\.?\s*([\w\d]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_po_at_no(self) -> str:
        """Extract PO/AT No."""
        patterns = [
            r'PO/AT\s*No\.\n\s*([\w\d\-]+)',
            r'PO/AT\s*No\.\s*([\w\d\-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_pl_no(self) -> str:
        """Extract PL No."""
        patterns = [
            r'PL\s*No\.\s*:\s*([\w\d\-]+)',
            r'PL\s*No\.\s*([\w\d\-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None


def analyze_receipt_pdf(pdf_path: str) -> Dict[str, Any]:
    """Convenience function to analyze a receipt PDF"""
    analyzer = PDFAnalyzer(pdf_path)
    return analyzer.analyze()
