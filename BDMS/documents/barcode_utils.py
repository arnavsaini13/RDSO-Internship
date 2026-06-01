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


def scan_barcode_from_image(image_file):
    """
    Scan and decode barcode from an image file
    
    Args:
        image_file: Image file (PIL Image, file path, or file object)
        
    Returns:
        barcode_data: Decoded barcode string or None if not found
    """
    try:
        # Load image based on input type
        if isinstance(image_file, str):
            # File path
            image = cv2.imread(image_file)
        elif isinstance(image_file, Image.Image):
            # PIL Image
            image = cv2.cvtColor(np.array(image_file), cv2.COLOR_RGB2BGR)
        else:
            # File object or similar
            image_array = np.frombuffer(image_file.read(), np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            return None
        
        # Convert to grayscale for better barcode detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply image processing to enhance barcode visibility
        # Use Otsu's thresholding
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Try to detect barcodes in the processed image
        detected_barcodes = pyzbar.decode(binary)
        
        # If no barcodes found in binary, try original image
        if not detected_barcodes:
            detected_barcodes = pyzbar.decode(image)
        
        # Return first detected barcode
        if detected_barcodes:
            return detected_barcodes[0].data.decode('utf-8')
        
        return None
        
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
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Try to detect barcodes
        detected_barcodes = pyzbar.decode(binary)
        
        if not detected_barcodes:
            detected_barcodes = pyzbar.decode(image)
        
        if detected_barcodes:
            return detected_barcodes[0].data.decode('utf-8')
        
        return None
        
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
