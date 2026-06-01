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
    from PyPDF2 import PdfReader
except ImportError:
    pass


class PDFAnalyzer:
    """Intelligent PDF Receipt Analyzer"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text = ""
        self.extracted_data = {}
    
    def extract_text_from_pdf(self) -> str:
        """Extract text from PDF using PyPDF2"""
        try:
            reader = PdfReader(self.pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text with PyPDF2: {e}")
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
            'batch_number': self._extract_batch_number(),
            'hsn_code': self._extract_hsn_code(),
            'description': self._extract_description(),
            'gst': self._extract_gst(),
            'invoice_number': self._extract_invoice_number(),
        }
        
        # Remove None values
        self.extracted_data = {k: v for k, v in self.extracted_data.items() if v is not None}
        
        return self.extracted_data
    
    def _extract_vendor_name(self) -> str:
        """Extract vendor/company name"""
        patterns = [
            r'(?:Vendor|Company|From|Supplier|Billed by|Seller)[\s:]*([^\n,]+)',
            r'[A-Z][A-Za-z\s&.,]+(?:Ltd|Limited|Inc|Corp|Company|Industries|Enterprises)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE | re.MULTILINE)
            if match:
                vendor = match.group(1).strip()
                if len(vendor) > 3 and len(vendor) < 200:
                    return vendor
        return None
    
    def _extract_material_name(self) -> str:
        """Extract material/product name"""
        patterns = [
            r'(?:Item|Product|Material|Description|Article)[\s:]*([^\n]+)',
            r'(?:^|\n)([A-Z][A-Za-z0-9\s]+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.MULTILINE)
            if match:
                material = match.group(1).strip()
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
    
    def _extract_batch_number(self) -> str:
        """Extract batch number"""
        patterns = [
            r'(?:Batch|Lot|Batch No|Batch Number|Lot No)[\s:]*([A-Za-z0-9\-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
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
        """Extract product description"""
        # Look for common description patterns
        lines = self.text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['description', 'product', 'item details']):
                if i + 1 < len(lines):
                    description = lines[i + 1].strip()
                    if description and len(description) > 5:
                        return description[:500]  # Limit to 500 chars
        return None
    
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
        patterns = [
            r'(?:Invoice|Bill|PO|Invoice No|Order No)[\s:#]*([A-Za-z0-9\-/]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                inv_no = match.group(1).strip()
                if len(inv_no) < 50:
                    return inv_no
        return None


def analyze_receipt_pdf(pdf_path: str) -> Dict[str, Any]:
    """Convenience function to analyze a receipt PDF"""
    analyzer = PDFAnalyzer(pdf_path)
    return analyzer.analyze()
