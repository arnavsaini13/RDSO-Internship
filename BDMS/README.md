# Barcode Document Management System (BDMS)

A professional government-style document management portal built with **Django**, **PostgreSQL**, and modern web technologies. BDMS automatically generates unique barcodes for uploaded PDFs, extracts text via OCR for scanned documents, and provides a secure, audit-logged interface for document management.

## Features

✅ **Document Management**
- Upload PDF documents with automatic barcode generation (Code128 format: DOC-2026-XXXX)
- Support for both text-based and scanned PDFs (with Tesseract OCR)
- Automatic text extraction for searchability
- Document status workflow (Pending → Verified → Approved → Archived)

✅ **Search & Retrieval**
- Multi-field search (barcode, title, content, department, category)
- Paginated results with filtering
- Fast document retrieval

✅ **Security & Audit Trail**
- User authentication and role-based access control (Admin/User)
- Transaction logging for all operations (upload, view, download, delete, barcode scan, search)
- IP address tracking for audit purposes

✅ **Government Portal Aesthetic**
- Professional dark blue and white color scheme (#1e3a5f, #003d82)
- Minimal, clean interface with soft shadows and smooth transitions
- Responsive Bootstrap 5 design
- Badge-based status indicators

✅ **Admin Dashboard**
- System statistics and overview
- Recent activity monitoring
- Department-based document distribution
- User and document management

## Technology Stack

- **Backend**: Django 6.0.5
- **Database**: PostgreSQL 18.0
- **Frontend**: Bootstrap 5.3.0, HTML5, CSS3, Vanilla JavaScript
- **PDF Processing**: PyPDF2, Tesseract OCR, pdf2image
- **Barcode Generation**: python-barcode (Code128)
- **Image Processing**: Pillow

## Installation & Setup

### Prerequisites

- **Python**: 3.10+
- **PostgreSQL**: 18.0+
- **pip**: Latest version
- **Tesseract OCR**: Version 5.x (for scanned PDF support)

### Step 1: Install System Dependencies

#### Windows

```powershell
# Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki
# Download and install the latest .exe file
# Default installation path: C:\Program Files\Tesseract-OCR

# Verify installation
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install libpq-dev
```

#### macOS

```bash
brew install tesseract
```

### Step 2: Create PostgreSQL Database & User

```powershell
# Open PostgreSQL terminal
psql -U postgres

# Create database
CREATE DATABASE bdms_db;

# Create user
CREATE USER arnavsaini13 WITH PASSWORD 'your_secure_password';

# Grant privileges
ALTER ROLE arnavsaini13 SET client_encoding TO 'utf8';
ALTER ROLE arnavsaini13 SET default_transaction_isolation TO 'read committed';
ALTER ROLE arnavsaini13 SET default_transaction_deferrable TO on;
ALTER ROLE arnavsaini13 SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE bdms_db TO arnavsaini13;

# Exit
\q
```

### Step 3: Clone & Setup Project

```bash
# Navigate to project directory
cd C:\RDSO Internship\BDMS

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 4: Configure Django Settings

Edit `BDMS/settings.py`:

```python
# Line ~90: Update database password
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bdms_db',
        'USER': 'arnavsaini13',
        'PASSWORD': 'your_secure_password',  # ← Set your password here
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Line ~160: Configure Tesseract path (Windows)
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Step 5: Run Database Migrations

```bash
# Create migrations for models
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Verify tables created
psql -U arnavsaini13 -d bdms_db -c "\dt"
```

### Step 6: Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@bdms.gov
# Password: (set secure password)
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

**Access the application:**
- Frontend: http://localhost:8000
- Admin Panel: http://localhost:8000/admin
- Login with superuser credentials

## Project Structure

```
BDMS/
├── BDMS/                          # Project configuration
│   ├── settings.py               # Django settings & database config
│   ├── urls.py                   # Main URL router
│   ├── wsgi.py                   # WSGI application
│   └── asgi.py                   # ASGI application
├── documents/                     # Core document management app
│   ├── models.py                 # Document, Transaction, UserProfile models
│   ├── views.py                  # Dashboard, upload, search, detail views
│   ├── forms.py                  # DocumentUploadForm, SearchForm, StatusForm
│   ├── urls.py                   # Document app URL routing
│   ├── admin.py                  # Admin panel configuration
│   ├── utils.py                  # Barcode generation, PDF processing, OCR
│   ├── apps.py                   # App configuration
│   └── templates/documents/
│       ├── dashboard.html        # System overview & statistics
│       ├── upload.html           # Document upload form
│       ├── search.html           # Search interface
│       ├── document_detail.html  # Document view with barcode
│       └── transactions.html     # Activity log & audit trail
├── users/                         # User authentication & profiles
│   ├── models.py                 # UserProfile model with roles
│   ├── views.py                  # Login, signup, profile views
│   ├── forms.py                  # SignUpForm, LoginForm, ProfileForm
│   ├── urls.py                   # User app URL routing
│   ├── admin.py                  # Admin panel configuration
│   ├── apps.py                   # App configuration
│   └── templates/users/
│       ├── login.html            # Login page
│       ├── signup.html           # User registration
│       └── profile.html          # User profile editor
├── templates/
│   └── base.html                 # Base template (navbar, footer, messages)
├── static/
│   ├── css/
│   │   └── style.css             # Government portal styling (500+ lines)
│   └── js/
│       └── main.js               # Client-side interactions
├── media/                         # Generated barcodes & uploaded PDFs
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Usage Guide

### User Workflows

#### 1. User Registration & Login

1. Navigate to http://localhost:8000/auth/signup/
2. Enter first name, last name, email, username, password
3. Click "Create Account"
4. Login at http://localhost:8000/auth/login/
5. View/edit profile at http://localhost:8000/auth/profile/

#### 2. Upload Document

1. Click "Upload Document" on dashboard
2. Enter document title, select department & category
3. Optionally add description
4. Select PDF file (max 10 MB)
5. Submit form
6. System automatically:
   - Generates unique barcode (DOC-2026-XXXX)
   - Creates Code128 barcode image
   - Extracts text from PDF (PyPDF2)
   - If scanned, performs OCR with Tesseract
   - Creates transaction log entry
7. Document status: **Pending** (awaiting verification)

#### 3. Search Documents

1. Click "Search" on navigation
2. Enter search query (barcode, title, or content)
3. Select search type (optional)
4. Filter by department, category, status
5. Click "Apply Filters"
6. Results paginated (10 per page)

#### 4. View Document Details

1. From search results or recent uploads, click "View"
2. Display shows:
   - Document metadata (title, department, category, uploaded by)
   - Code128 barcode with copy button
   - Extracted text preview
   - Transaction history
3. Admin can: Update status, add remarks
4. Owner/Admin can: Delete document

#### 5. Download Document

1. On document detail page, click "Download PDF"
2. Original PDF saved to local machine

#### 6. View Activity Log

1. Click "Activities" or navigate to /documents/transactions/
2. View all system transactions
3. Filter by action type, user, date
4. Track all document operations

### Admin Workflows

#### 1. Admin Panel

1. Navigate to http://localhost:8000/admin
2. Login with superuser credentials
3. Manage:
   - **Documents**: View, filter by status, search
   - **Transactions**: Audit trail with timestamps
   - **Users**: View roles, departments, activate/deactivate

#### 2. Document Verification

1. Dashboard shows pending documents
2. Click on pending document
3. Review extracted text and barcode
4. Click "Update Status"
5. Change to "Verified" or "Approved"
6. Add remarks if needed
7. Save changes (logs transaction)

#### 3. User Management

1. Users → Profiles in admin
2. Assign departments and roles
3. Activate/deactivate user accounts
4. Reset credentials via Django's auth system

## API Endpoints

### Documents App

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/documents/` | Dashboard overview |
| GET | `/documents/upload/` | Upload form page |
| POST | `/documents/upload/` | Process uploaded document |
| GET | `/documents/search/` | Search interface |
| POST | `/documents/search/` | Perform search |
| GET | `/documents/document/<id>/` | View document details |
| GET | `/documents/document/<id>/download/` | Download PDF |
| POST | `/documents/document/<id>/delete/` | Delete document |
| POST | `/documents/document/<id>/status/` | Update status (admin only) |
| GET | `/documents/barcode/<barcode_value>/` | Retrieve by barcode |
| GET | `/documents/transactions/` | Activity log |

### Users App

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/auth/login/` | Login page |
| POST | `/users/auth/login/` | Process login |
| GET | `/users/auth/signup/` | Registration page |
| POST | `/users/auth/signup/` | Create new user |
| GET | `/users/auth/logout/` | Logout user |
| GET | `/users/auth/profile/` | View profile |
| POST | `/users/auth/profile/` | Update profile |

## Key Features Explained

### Barcode Generation

- **Format**: Code128 (DOC-2026-XXXX)
- **Generation**: Automatic on document upload
- **Image**: PNG file stored in media folder
- **Display**: Barcode shown on document detail page with copy button

### Text Extraction

**Text-Based PDFs**:
- Uses PyPDF2 library
- Extracts all page text
- Fast processing

**Scanned PDFs**:
- Detects if PDF is image-based
- Converts pages to images with pdf2image
- Uses Tesseract OCR for text extraction
- More time-intensive but accurate

### Transaction Logging

Every action logged with:
- User who performed action
- Action type (UPLOAD, VIEW, DOWNLOAD, DELETE, BARCODE_SCAN, SEARCH)
- Associated document
- Timestamp
- IP address
- Optional remarks

### Document Status Workflow

1. **PENDING**: Just uploaded, awaiting admin verification
2. **VERIFIED**: Admin confirmed document authenticity
3. **APPROVED**: Approved for official use
4. **ARCHIVED**: Document retired but preserved for audit trail

## Troubleshooting

### Issue: PostgreSQL Connection Refused

```
Solution:
1. Verify PostgreSQL running: pg_isready -h localhost
2. Check credentials in settings.py
3. Ensure user has database access: GRANT ALL PRIVILEGES ON DATABASE bdms_db TO arnavsaini13;
4. Restart PostgreSQL service
```

### Issue: Tesseract Not Found

```
Solution:
1. Verify installation: "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
2. Update settings.py with correct path
3. Restart Django development server
```

### Issue: Barcode Not Generating

```
Solution:
1. Check media/ directory exists and is writable
2. Verify python-barcode installed: pip show python-barcode
3. Check document PDF file is valid
```

### Issue: File Upload Fails

```
Solution:
1. Ensure media/ directory exists
2. Check file size < 10 MB
3. Verify PDF format (not corrupted)
4. Check disk space available
```

## Performance Optimization

- Database indexes on barcode_value and status fields
- Paginated search results (10 per page)
- Django query optimization with select_related/prefetch_related
- Static file caching headers
- Compressed CSS and JavaScript

## Security Features

- CSRF protection on all forms
- SQL injection prevention via Django ORM
- User authentication required (@login_required)
- Role-based access control
- Password hashing with Django auth
- IP address logging for audit trail
- Transaction log for accountability

## Future Enhancements

- Batch document upload
- Advanced search with full-text search (PostgreSQL FTS)
- Document version control
- Email notifications
- API token authentication
- Document digitally signing
- Integration with external document systems
- Multi-language support
- Advanced analytics dashboard

## Support & Documentation

For detailed documentation:
- Django: https://docs.djangoproject.com/en/6.0/
- PostgreSQL: https://www.postgresql.org/docs/18/
- Bootstrap: https://getbootstrap.com/docs/5.3/
- PyPDF2: https://pypi.org/project/PyPDF2/
- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki

## License

Government of India - Internal Use Only

## Author

RDSO Internship Project Team
