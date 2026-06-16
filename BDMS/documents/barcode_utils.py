"""
Barcode Generation and Scanning Utilities
Handles barcode creation for materials and scanning/decoding
"""

import os
import io
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import barcode
from barcode.writer import ImageWriter
from pyzbar import pyzbar
from django.core.files.base import ContentFile
from django.conf import settings


def generate_material_barcode(material):
    """
    Generate barcode image for a material and save it
    
    Args:
        material: Material instance
        
    Returns:
        barcode_image_path: Path to the generated barcode image file
    """
    try:
        # Use material_id as barcode data
        barcode_data = material.material_id
        
        # Create barcode (use CODE128 format - widely compatible)
        barcode_class = barcode.get_barcode_class('code128')
        barcode_instance = barcode_class(barcode_data, writer=ImageWriter())
        
        # Generate barcode image in memory
        barcode_buffer = io.BytesIO()
        barcode_instance.write(barcode_buffer)
        barcode_buffer.seek(0)
        
        # Convert to PIL Image and save
        barcode_image = Image.open(barcode_buffer)
        
        # Convert to RGB if necessary (barcode generates grayscale)
        if barcode_image.mode != 'RGB':
            barcode_image = barcode_image.convert('RGB')
        
        # Save to Django FileField
        image_io = io.BytesIO()
        barcode_image.save(image_io, format='PNG')
        image_io.seek(0)
        
        # Save to material
        filename = f"{material.material_id}_barcode.png"
        material.barcode_image.save(filename, ContentFile(image_io.read()), save=False)
        material.barcode_data = barcode_data
        
        return material.barcode_image.path if material.barcode_image else None
        
    except Exception as e:
        print(f"Error generating barcode for {material.material_id}: {str(e)}")
        return None


def _decode_barcode_image(image) -> str:
    """
    Decodes barcode from an OpenCV image using multiple image processing techniques
    to ensure extremely robust detection under blurry, low-light, or high-contrast settings.
    Includes transparent PNG alpha-blending and automatic quiet-zone border padding.
    """
    if image is None:
        return None
        
    try:
        # Handle transparent PNG alpha-channel (4 channels BGRA)
        if len(image.shape) == 3 and image.shape[2] == 4:
            b, g, r, a = cv2.split(image)
            alpha_factor = a.astype(float) / 255.0
            # Blend BGR channels with white background where transparent
            b = (b.astype(float) * alpha_factor + 255.0 * (1.0 - alpha_factor)).astype(np.uint8)
            g = (g.astype(float) * alpha_factor + 255.0 * (1.0 - alpha_factor)).astype(np.uint8)
            r = (r.astype(float) * alpha_factor + 255.0 * (1.0 - alpha_factor)).astype(np.uint8)
            image = cv2.merge([b, g, r])
    except Exception as e:
        print(f"Error blending transparent channel: {e}")
        
    def try_decoding_variants(img_to_test) -> str:
        # Convert to Grayscale
        if len(img_to_test.shape) == 3:
            gray_img = cv2.cvtColor(img_to_test, cv2.COLOR_BGR2GRAY)
        else:
            gray_img = img_to_test
            
        # 1. Try original/grayscale direct decode
        decoded = pyzbar.decode(img_to_test)
        if decoded:
            return decoded[0].data.decode('utf-8')
        decoded = pyzbar.decode(gray_img)
        if decoded:
            return decoded[0].data.decode('utf-8')
            
        # 2. Otsu Global Thresholding (excellent for high contrast)
        _, binary = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        decoded = pyzbar.decode(binary)
        if decoded:
            return decoded[0].data.decode('utf-8')
            
        # 3. Adaptive Gaussian Thresholding (excellent for uneven lighting/shadows)
        adaptive = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        decoded = pyzbar.decode(adaptive)
        if decoded:
            return decoded[0].data.decode('utf-8')
            
        # 4. Rescaling 2x (resolves small/thin lines)
        h, w = gray_img.shape[:2]
        resized = cv2.resize(gray_img, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
        decoded = pyzbar.decode(resized)
        if decoded:
            return decoded[0].data.decode('utf-8')
            
        # 5. Rescaling 3x with Otsu Binarization (vital for low-res screenshots!)
        resized_3x = cv2.resize(gray_img, (w * 3, h * 3), interpolation=cv2.INTER_CUBIC)
        decoded = pyzbar.decode(resized_3x)
        if decoded:
            return decoded[0].data.decode('utf-8')
            
        _, binary_3x = cv2.threshold(resized_3x, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        decoded = pyzbar.decode(binary_3x)
        if decoded:
            return decoded[0].data.decode('utf-8')
            
        # 6. Gaussian Blur + Thresholding (removes camera noise)
        blurred = cv2.GaussianBlur(gray_img, (5, 5), 0)
        _, binary_blur = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        decoded = pyzbar.decode(binary_blur)
        if decoded:
            return decoded[0].data.decode('utf-8')
            
        return None

    # Step A: Try decoding the original cropped/raw image
    result = try_decoding_variants(image)
    if result:
        return result

    # Step B: If failed, add a virtual solid white border (Quiet Zone) on all sides.
    # Barcode scanning standards require a clear blank margin on the left/right of lines.
    # Cropped or pasted screenshots typically cut this off, causing the scanner to fail.
    try:
        padded = cv2.copyMakeBorder(
            image, 
            top=35, 
            bottom=35, 
            left=35, 
            right=35, 
            borderType=cv2.BORDER_CONSTANT, 
            value=[255, 255, 255]
        )
        result = try_decoding_variants(padded)
        if result:
            return result
    except Exception as e:
        print(f"Error applying border padding: {e}")

    return None


def scan_barcode_from_image(image_file):
    """
    Scan and decode barcode from an image file or PDF file
    
    Args:
        image_file: Image file (PIL Image, file path, file object, or PDF file)
        
    Returns:
        barcode_data: Decoded barcode string or None if not found
    """
    try:
        # Check if the input file is a PDF
        is_pdf = False
        if isinstance(image_file, str) and image_file.lower().endswith('.pdf'):
            is_pdf = True
        elif hasattr(image_file, 'name') and image_file.name.lower().endswith('.pdf'):
            is_pdf = True
            
        if is_pdf:
            # Handle PDF file natively using PyMuPDF (fitz) - no Poppler required!
            import fitz
            if isinstance(image_file, str):
                pdf_doc = fitz.open(image_file)
            else:
                image_file.seek(0)
                pdf_bytes = image_file.read()
                pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                
            for page in pdf_doc:
                # Render page at 4x zoom (~300 DPI) for high precision barcode detection
                zoom = 4
                zoom_mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=zoom_mat)
                img_bytes = pix.tobytes("png")
                image_array = np.frombuffer(img_bytes, np.uint8)
                cv_img = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)
                
                data = _decode_barcode_image(cv_img)
                if data:
                    pdf_doc.close()
                    return data
                    
            pdf_doc.close()
            return None

        # Standard Image file handling
        if isinstance(image_file, str):
            image = cv2.imread(image_file, cv2.IMREAD_UNCHANGED)
        elif isinstance(image_file, Image.Image):
            image = cv2.cvtColor(np.array(image_file), cv2.COLOR_RGB2BGR)
        else:
            # File object or similar
            image_file.seek(0)
            image_array = np.frombuffer(image_file.read(), np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)
        
        return _decode_barcode_image(image)
        
    except Exception as e:
        print(f"Error scanning barcode: {str(e)}")
        return None


def scan_barcode_from_camera():
    """
    Capture image from webcam and scan for barcode
    NOTE: This is for backend processing - frontend handles camera access via JavaScript
    
    Returns:
        barcode_data: Decoded barcode string or None
    """
    try:
        # Open webcam
        camera = cv2.VideoCapture(0)
        
        if not camera.isOpened():
            return None
        
        barcode_data = None
        max_attempts = 30  # Try for ~1 second at 30 FPS
        
        while max_attempts > 0:
            ret, frame = camera.read()
            
            if not ret:
                break
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Try to detect barcodes
            detected_barcodes = pyzbar.decode(binary)
            
            if not detected_barcodes:
                detected_barcodes = pyzbar.decode(frame)
            
            if detected_barcodes:
                barcode_data = detected_barcodes[0].data.decode('utf-8')
                break
            
            max_attempts -= 1
        
        camera.release()
        return barcode_data
        
    except Exception as e:
        print(f"Error scanning from camera: {str(e)}")
        return None


def process_canvas_image(canvas_data: str):
    """
    Process base64 encoded image data from canvas/camera capture
    
    Args:
        canvas_data: Base64 encoded image data from canvas (data:image/png;base64,...)
        
    Returns:
        barcode_data: Decoded barcode string or None
    """
    try:
        import base64
        
        # Remove data URL prefix if present
        if ',' in canvas_data:
            canvas_data = canvas_data.split(',')[1]
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(canvas_data)
        image_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)
        
        return _decode_barcode_image(image)
        
    except Exception as e:
        print(f"Error processing canvas image: {str(e)}")
        return None


def get_material_by_barcode(barcode_data):
    """
    Retrieve material information using barcode data
    
    Args:
        barcode_data: Barcode string to search for
        
    Returns:
        material: Material instance or None
    """
    try:
        from .models import Material
        # First try exact match on barcode_data field
        material = Material.objects.filter(barcode_data=barcode_data).first()
        
        # If not found, try material_id (barcode stores material_id)
        if not material:
            material = Material.objects.filter(material_id=barcode_data).first()
        
        return material
        
    except Exception as e:
        print(f"Error retrieving material by barcode: {str(e)}")
        return None


def regenerate_barcode(material):
    """
    Regenerate barcode for an existing material
    
    Args:
        material: Material instance
        
    Returns:
        success: Boolean indicating success
    """
    try:
        # Delete old barcode if exists
        if material.barcode_image and material.barcode_image.name:
            try:
                material.barcode_image.delete()
            except:
                pass
        
        # Generate new barcode
        barcode_path = generate_material_barcode(material)
        material.save()
        
        return barcode_path is not None
        
    except Exception as e:
        print(f"Error regenerating barcode: {str(e)}")
        return False
