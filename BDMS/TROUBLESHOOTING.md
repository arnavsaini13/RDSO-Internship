# BDMS Troubleshooting Decision Tree & Solutions

## 🆘 Problem Diagnostic Guide

This guide helps you identify and fix problems yourself!

---

## **🔴 ISSUE: PostgreSQL Error - "psql is not recognized"**

### Symptoms:
```
'psql' is not recognized as an internal or external command
```

### Root Cause:
PostgreSQL bin directory is not in system PATH

### Solution 1: Use Full Path (Quickest)
```powershell
cd "C:\Program Files\PostgreSQL\18\bin"
.\psql -U postgres
```

### Solution 2: Add to PATH Permanently
```powershell
# Add to current session path
$env:Path += ";C:\Program Files\PostgreSQL\18\bin"

# Now try:
psql -U postgres
```

### Solution 3: Verify PostgreSQL Installation
```powershell
# Check if PostgreSQL is installed at expected location
Test-Path "C:\Program Files\PostgreSQL\18\bin\psql.exe"

# If returns: False
# Then PostgreSQL is installed elsewhere
# Search for it: Get-ChildItem -Path "C:\" -Name "*PostgreSQL*" -Directory
```

### ✅ Expected Success:
```
psql (18.0)
Type "help" for help.
postgres=#
```

---

## **🔴 ISSUE: PostgreSQL Error - "FATAL: password authentication failed"**

### Symptoms:
```
FATAL: password authentication failed for user "postgres"
FATAL: Ident authentication failed for user "arnavsaini13"
```

### Root Cause:
Wrong password or authentication method

### Diagnostic Flowchart:
```
Q1: Are you logging in as "postgres"?
├─ YES → Did you use your PostgreSQL admin password?
│        (Set during PostgreSQL installation)
│        ├─ YES → Try resetting:
│        │         • Use pg_ctl to reset
│        │         • Or reinstall PostgreSQL
│        │         • Contact system admin
│        │
│        └─ NO → Try again with correct password
│
└─ NO → Are you logging in as "arnavsaini13"?
        └─ YES → Did you use the password from Step 2.3?
                 ├─ YES → Password matches in settings.py?
                 │        ├─ YES → Check pg_hba.conf authentication method
                 │        │         (Should be "md5" or "scram-sha-256")
                 │        │
                 │        └─ NO → Update settings.py with exact password
                 │
                 └─ NO → Try with the password you created
```

### Solution 1: Verify You Set the Password
```sql
-- Login as postgres (you know this password)
-- Then reset the arnavsaini13 user password:

ALTER USER arnavsaini13 WITH PASSWORD 'new_password';

-- Example:
ALTER USER arnavsaini13 WITH PASSWORD 'MyNewPass456!';

-- Then update this password in settings.py
```

### Solution 2: Check settings.py Password
```python
# Open BDMS/settings.py
# Find DATABASES section
# Check PASSWORD line:

'PASSWORD': 'MySecurePass123!',

# Make sure:
# - No extra spaces before/after
# - Exactly matches PostgreSQL password
# - Right quotation marks (')
# - No typos
```

### Solution 3: Test Connection Manually
```powershell
# Test if credentials work
psql -h localhost -U arnavsaini13 -d bdms_db

# Enter password when prompted
# If successful, you'll see: bdms_db=>
```

### ✅ Expected Success:
```
psql (18.0)
Type "help" for help.

bdms_db=>
```

---

## **🔴 ISSUE: Django Error - "could not connect to the database"**

### Symptoms:
```
django.db.utils.OperationalError: could not connect to server: 
Connection refused. Is the server running on host "localhost" (127.0.0.1) 
port 5432?
```

### Root Cause Flowchart:
```
Is PostgreSQL running?
├─ NO → Start PostgreSQL service
│       Windows: Services → postgresql-x64-18 → Start
│
├─ YES → Is database "bdms_db" created?
│        ├─ NO → Create it: CREATE DATABASE bdms_db;
│        │
│        └─ YES → Is user "arnavsaini13" created?
│                 ├─ NO → Create it: CREATE USER arnavsaini13...
│                 │
│                 └─ YES → Check settings.py DATABASE config
│                          ├─ NAME: bdms_db ✓
│                          ├─ USER: arnavsaini13 ✓
│                          ├─ PASSWORD: matches ✓
│                          ├─ HOST: localhost ✓
│                          └─ PORT: 5432 ✓
```

### Solution 1: Check if PostgreSQL is Running
```powershell
# Windows - Check PostgreSQL service
Get-Service -Name postgresql-x64-18

# Output should show:
# Status   Name
# ------   ----
# Running  postgresql-x64-18

# If not running:
Start-Service -Name postgresql-x64-18
```

### Solution 2: Check Connection
```powershell
# Test PostgreSQL connection
pg_isready -h localhost -p 5432

# Expected output:
# accepting connections

# If says "rejecting connections":
# PostgreSQL isn't properly running
# Restart service:
Restart-Service -Name postgresql-x64-18 -Force
```

### Solution 3: Verify settings.py Configuration
```python
# BDMS/settings.py around line 85-95
# Should look exactly like:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bdms_db',
        'USER': 'arnavsaini13',
        'PASSWORD': 'YourActualPassword',  # ← Your password here
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Common mistakes:
# ❌ 'PASSWORD': ''  (empty)
# ❌ 'HOST': '127.0.0.1' (use 'localhost' instead)
# ❌ 'PORT': '5432' (with quotes - OK, without - OK too)
```

### Solution 4: Test Django Connection
```powershell
# Navigate to BDMS folder
cd "C:\RDSO Internship\BDMS"

# Activate venv
.\venv\Scripts\Activate.ps1

# Test database connection
python manage.py dbshell

# You should see:
# psql (18.0)
# bdms_db=> 

# Type \q to exit
```

### ✅ When Fixed:
```
python manage.py runserver
# Should start without database errors
```

---

## **🔴 ISSUE: Tesseract Error - "tesseract is not installed"**

### Symptoms:
```
TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

### This happens when:
- Uploading a scanned PDF
- Tesseract is not installed
- Or wrong path in settings.py

### Solution 1: Verify Tesseract Installation
```powershell
# Check if Tesseract exists
Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe"

# Expected output: True
# If False: Tesseract not installed at default location

# Try running directly
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version

# Should show version info
```

### Solution 2: Find Tesseract Installation
```powershell
# Search entire C: drive for Tesseract
Get-ChildItem -Path "C:\" -Name "*Tesseract*" -Directory -Recurse

# Or search for the executable:
Get-ChildItem -Path "C:\" -Name "tesseract.exe" -File -Recurse
```

### Solution 3: Update settings.py with Correct Path
```python
# BDMS/settings.py around line 160

# Current (if wrong):
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Change to your actual path:
# Example if installed in D:\
pytesseract.pytesseract.pytesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'

# Save file: Ctrl+S
```

### Solution 4: Reinstall Tesseract
```
1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download latest installer
3. Run installer
4. Accept default path: C:\Program Files\Tesseract-OCR
5. Verify with: "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
6. Restart Django server
```

### ✅ When Fixed:
- Text-based PDFs upload fine
- Scanned PDFs upload and OCR processes them
- No more TesseractNotFoundError

---

## **🔴 ISSUE: Port 8000 Already in Use**

### Symptoms:
```
Error: That port is already in use.
OSError: [Errno 48] Address already in use
```

### Root Cause:
Another application is using port 8000

### Solution 1: Use Different Port
```powershell
# Instead of:
python manage.py runserver

# Use:
python manage.py runserver 8001

# Access at: http://localhost:8001
# Or try 8002, 8003, etc.
```

### Solution 2: Find What's Using Port 8000
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Output shows process ID (PID)
# Example: TCP    127.0.0.1:8000    0.0.0.0:0    LISTENING    12345

# Kill the process:
taskkill /PID 12345 /F

# Then try: python manage.py runserver
```

### Solution 3: Stop Previous Django Server
```
If you left Django running in another terminal:
- Find that terminal window
- Press Ctrl+C to stop it
- Now you can start fresh
```

---

## **🔴 ISSUE: Virtual Environment Not Activating**

### Symptoms:
```
You don't see (venv) at the start of PowerShell prompt
```

### Root Cause:
venv not in project folder OR activation script failed

### Diagnostic:
```powershell
# Check if venv exists
Test-Path "C:\RDSO Internship\BDMS\venv"

# If False: venv doesn't exist, create it:
cd "C:\RDSO Internship\BDMS"
python -m venv venv

# Then activate:
.\venv\Scripts\Activate.ps1
```

### Solution 1: Create Virtual Environment
```powershell
# Navigate to BDMS
cd "C:\RDSO Internship\BDMS"

# Create venv
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Verify: should see (venv) at prompt start
```

### Solution 2: Execution Policy Issue
```powershell
# If activation script won't run due to policy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try:
.\venv\Scripts\Activate.ps1
```

### Solution 3: Manual Activation
```powershell
# If above doesn't work:
.\venv\Scripts\Activate.bat

# (uses .bat instead of .ps1)
```

### ✅ Success Indicators:
```
(venv) PS C:\RDSO Internship\BDMS>
# This shows venv is active
```

---

## **🔴 ISSUE: "ModuleNotFoundError: No module named 'django'"**

### Symptoms:
```
ModuleNotFoundError: No module named 'django'
or
No module named 'psycopg2'
No module named 'barcode'
```

### Root Cause:
- Packages not installed
- venv not activated
- Wrong Python version

### Diagnostic Flowchart:
```
Is venv activated?
├─ NO → Activate: .\venv\Scripts\Activate.ps1
│
└─ YES → Are packages installed?
        ├─ NO → Install: pip install -r requirements.txt
        │
        └─ YES → Check Python version:
                 └─ python --version
                    Should be 3.10 or higher
```

### Solution 1: Ensure venv is Active
```powershell
# Must see (venv) at prompt start
# If not:
cd "C:\RDSO Internship\BDMS"
.\venv\Scripts\Activate.ps1

# Verify: (venv) should now show
```

### Solution 2: Reinstall All Packages
```powershell
# Make sure venv is active
.\venv\Scripts\Activate.ps1

# Upgrade pip first
python -m pip install --upgrade pip

# Install packages
pip install -r requirements.txt

# Verify installation
pip list
# Should show: Django, psycopg2-binary, PyPDF2, etc.
```

### Solution 3: Check Python Version
```powershell
python --version

# Should be 3.10 or higher
# If 3.9 or lower:
# Either upgrade Python or install Python 3.10+ separately
```

### Solution 4: Force Reinstall
```powershell
# If issues persist:
pip install --force-reinstall -r requirements.txt

# This takes longer but fixes most issues
```

### ✅ When Fixed:
```
pip list
# Shows all packages installed

python -c "import django; print(django.get_version())"
# Shows: 6.0.5
```

---

## **🔴 ISSUE: Syntax Error in settings.py**

### Symptoms:
```
SyntaxError: invalid syntax
or
ConfigurationError: ...
```

### Root Cause:
Mistake when editing settings.py

### Common Mistakes:
```python
# ❌ Missing quote
'PASSWORD': your_password,
# ✅ Correct:
'PASSWORD': 'your_password',

# ❌ Missing colon
'HOST' 'localhost'
# ✅ Correct:
'HOST': 'localhost',

# ❌ Wrong bracket type
'PASSWORD': 'pass'
# ✅ Correct (use regular quotes):
'PASSWORD': 'pass',

# ❌ No comma between items
'USER': 'arnavsaini13'
'PASSWORD': 'pass'
# ✅ Correct:
'USER': 'arnavsaini13',
'PASSWORD': 'pass',
```

### Solution: Compare with Template
```python
# Your settings.py should look EXACTLY like this
# (replace with your actual password):

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bdms_db',
        'USER': 'arnavsaini13',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### How to Find Syntax Error:
```powershell
# Python can tell you where the error is:
python -m py_compile BDMS/settings.py

# If syntax OK, no output
# If error, shows line number:
# SyntaxError: invalid syntax (settings.py, line 95)

# Then check that line for mistakes
```

---

## **🔴 ISSUE: Login Page Won't Load**

### Symptoms:
```
Page won't load
Blank page
Error 500
```

### Diagnostic Steps:

**Step 1: Check Server Terminal**
```
If using: python manage.py runserver
Look at terminal for error messages

Example error:
  File "BDMS/settings.py", line 95, in <module>
    SyntaxError: invalid syntax
```

**Step 2: Check Browser Developer Tools**
```
Press F12 in browser
Click "Console" tab
Look for JavaScript errors (unlikely to be the issue)
```

**Step 3: Verify Server is Running**
```
Should see:
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Common Causes:
```
❌ Database not connected
   → Check settings.py DATABASE section
   → Check PostgreSQL is running

❌ Migrations not applied
   → Run: python manage.py migrate

❌ Static files not collected
   → Run: python manage.py collectstatic --noinput

❌ settings.py has error
   → Check syntax with: python -m py_compile BDMS/settings.py
```

### Solution:
```powershell
# Start fresh:
# 1. Stop server (Ctrl+C in terminal)

# 2. Check settings.py syntax:
python -m py_compile BDMS/settings.py

# 3. Run migrations:
python manage.py migrate

# 4. Restart server:
python manage.py runserver

# 5. Try loading: http://localhost:8000
```

---

## **🔴 ISSUE: Can't Login - "Invalid username or password"**

### Symptoms:
```
Authentication failed
Invalid username or password
```

### Diagnostic:
```
Did you enter:
  Username: admin (exactly as created)
  Password: (exactly as you set it)

Check for:
  • Caps lock on?
  • Extra spaces?
  • Correct special characters?
```

### Solution 1: Verify Admin Account Exists
```powershell
# Check if admin user was created
python manage.py shell

# In Python shell, type:
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username='admin').exists()

# Should return: True

# If False: admin wasn't created
# Exit shell: >>> exit()
# Recreate: python manage.py createsuperuser
```

### Solution 2: Reset Admin Password
```powershell
python manage.py shell

# In Python shell:
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='admin')
>>> user.set_password('newpassword123')
>>> user.save()

# Now try login with new password
# Exit: >>> exit()
```

### Solution 3: Check for Typos
```
Common typos:
❌ Login with "Admin" (capital A) - case sensitive!
   ✅ Use "admin" (lowercase)

❌ Using wrong email or username
   ✅ Use exactly "admin"

❌ Space in password
   ✅ No spaces allowed
```

---

## **🔴 ISSUE: Can't Upload PDF - "File validation failed"**

### Symptoms:
```
The file must be a PDF
File size exceeds limit
```

### Solution 1: Check File Format
```
File must be:
✅ PDF format (.pdf extension)
❌ Not images (.jpg, .png)
❌ Not Word documents (.docx)
❌ Not other formats

Solution: Convert to PDF first if needed
```

### Solution 2: Check File Size
```
Maximum: 10 MB

If your file is larger:
- Compress PDF
- Split PDF into smaller files
- Try uploading smaller document first
```

### Solution 3: Check File Isn't Corrupted
```
If PDF is corrupted:
- Try opening it in Adobe Reader
- If won't open, file is corrupted
- Re-download or re-scan document
```

---

## **🔴 ISSUE: Barcode Not Generating**

### Symptoms:
```
Document uploads but no barcode image
Barcode field shows null/empty
```

### Diagnostic:
```
1. Check media folder exists:
   C:\RDSO Internship\BDMS\media\barcodes\

2. If folder doesn't exist:
   Create it manually

3. Check barcode_value in database:
   python manage.py shell
   >>> from documents.models import Document
   >>> doc = Document.objects.first()
   >>> print(doc.barcode_value)
   (Should show: DOC-2026-0001)
```

### Solution 1: Create Media Directories
```powershell
# Navigate to BDMS
cd "C:\RDSO Internship\BDMS"

# Create media directories if missing
mkdir -p media\barcodes
mkdir -p media\pdfs

# Give permissions (Windows already does this)
```

### Solution 2: Check Barcode Library
```powershell
# Verify python-barcode installed
pip list | findstr barcode

# Should show: python-barcode  0.15.1

# If not:
pip install python-barcode==0.15.1
```

### Solution 3: Try Uploading Again
```
- Create new document
- Fill in all fields
- Upload PDF
- Check barcode generates
```

---

## **🔴 ISSUE: OCR Not Working on Scanned PDFs**

### Symptoms:
```
Scanned PDF uploaded but text not extracted
is_scanned shows False when should be True
```

### Diagnostic:
```
1. Tesseract installed?
   "C:\Program Files\Tesseract-OCR\tesseract.exe" --version

2. Path correct in settings.py?
   pytesseract.pytesseract.pytesseract_cmd = r'C:\...'

3. pdf2image installed?
   pip list | findstr pdf2image
```

### Solution 1: Verify Tesseract Installation
```powershell
# Check installation
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version

# If not found:
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Run installer and try again
```

### Solution 2: Restart Django Server
```powershell
# After installing/updating:
# 1. Stop server: Ctrl+C
# 2. Start server: python manage.py runserver
# 3. Try uploading again
```

### Solution 3: Check PDF is Actually Scanned
```
Not all "scanned" PDFs are image-based.
Some are still text-based but look like scans.

Try with a known scanned PDF:
- Scan document with scanner
- Save as PDF
- Upload to BDMS
```

---

## **📊 Quick Reference: Error → Solution Map**

| Error | Solution |
|-------|----------|
| `psql is not recognized` | Use full path: `C:\Program Files\PostgreSQL\18\bin\psql` |
| `password authentication failed` | Check settings.py PASSWORD matches PostgreSQL |
| `could not connect to database` | Verify PostgreSQL is running, START PostgreSQL service |
| `tesseract not found` | Install from github.com/UB-Mannheim/tesseract |
| `port 8000 in use` | Use different port: `runserver 8001` |
| `ModuleNotFoundError` | Activate venv: `.\venv\Scripts\Activate.ps1` |
| `SyntaxError in settings.py` | Check quotes, colons, commas |
| `Login fails` | Verify admin account: `python manage.py shell` |
| `File validation failed` | Check file is PDF under 10 MB |
| `Barcode not generating` | Create media/barcodes/ folder |
| `OCR not working` | Verify Tesseract installed and path correct |

---

## **🆘 If All Else Fails**

### Nuclear Option: Complete Reset
```powershell
# WARNING: This deletes everything and starts fresh

# 1. Stop Django server (Ctrl+C)

# 2. Delete database
cd "C:\Program Files\PostgreSQL\18\bin"
.\psql -U postgres
DROP DATABASE bdms_db;
DROP USER arnavsaini13;
\q

# 3. Delete Python cache
cd "C:\RDSO Internship\BDMS"
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force

# 4. Delete media files
Remove-Item -Path media -Recurse

# 5. Recreate venv
Remove-Item -Path venv -Recurse
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 6. Start over from Step 2 of SETUP_GUIDE_DETAILED.md
```

### Ask For Help
If still stuck, provide:
```
1. Exact error message (copy-paste from terminal)
2. What step you're on
3. What you tried to fix it
4. Screenshots if possible
5. System info: Windows version, Python version
```

---

**Remember:** Most errors have simple solutions - take a breath and check the checklists above! 🧠
