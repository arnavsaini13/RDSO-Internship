# BDMS Setup Guide - Step-by-Step for Beginners

## 📚 Table of Contents
1. Install Tesseract OCR
2. Create PostgreSQL Database
3. Install Python Dependencies
4. Configure Django Settings
5. Run Database Migrations
6. Create Admin Account
7. Start the Server
8. Access the Application

---

## **STEP 1: Install Tesseract OCR** ⚙️

**What is Tesseract OCR?**
- OCR = Optical Character Recognition
- It reads text from scanned PDF images
- BDMS uses it to extract text from scanned documents

### On Windows:

**1.1 Download Tesseract**
```
1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Look for "Downloads" section
3. Download the latest .exe file (e.g., tesseract-ocr-w64-setup-v5.3.exe)
4. File size: ~200-300 MB
```

**1.2 Run the Installer**
```
1. Double-click the downloaded .exe file
2. Click "Next >" through the installer screens
3. Accept the default installation path: C:\Program Files\Tesseract-OCR
4. Click "Install"
5. Wait for installation to complete (2-3 minutes)
6. Click "Finish"
```

**1.3 Verify Installation**
```powershell
# Open PowerShell (Right-click Start → Windows PowerShell)
# Run this command:

"C:\Program Files\Tesseract-OCR\tesseract.exe" --version

# Expected output:
# tesseract 5.3.0
# leptonica-1.82.0
# ...

# If you see version info, Tesseract is installed correctly ✓
```

**If installation path is different:**
- During setup, note the custom path you chose
- You'll use this path in Step 4 (Django configuration)

---

## **STEP 2: Create PostgreSQL Database** 🗄️

**What is PostgreSQL?**
- Database system that stores all your documents, users, and transactions
- Like a spreadsheet but much more powerful
- BDMS stores everything here

**Prerequisites:** PostgreSQL 18.0 must be installed (you should have it already)

### On Windows:

**2.1 Open PostgreSQL Command Line**
```powershell
# Option A: Using PowerShell (Recommended for beginners)
# Run these commands one by one:

# First, navigate to PostgreSQL installation
cd "C:\Program Files\PostgreSQL\18\bin"

# Start PostgreSQL terminal (will prompt for password)
.\psql -U postgres

# Enter your PostgreSQL admin password (created during PostgreSQL installation)
# After entering password, you'll see: postgres=#
```

**2.2 Create Database**
```sql
-- At the postgres=# prompt, type this command and press Enter:
CREATE DATABASE bdms_db;

-- Expected output:
-- CREATE DATABASE

-- This creates an empty database named "bdms_db"
```

**2.3 Create User Account**
```sql
-- At the postgres=# prompt, type this command:
CREATE USER arnavsaini13 WITH PASSWORD 'your_secure_password';

-- Replace 'your_secure_password' with a password you'll remember
-- Example: CREATE USER arnavsaini13 WITH PASSWORD 'MySecurePass123!';

-- Expected output:
-- CREATE ROLE
```

**2.4 Grant Database Privileges**
```sql
-- At the postgres=# prompt, type these commands one by one:

ALTER ROLE arnavsaini13 SET client_encoding TO 'utf8';
-- Output: ALTER ROLE

ALTER ROLE arnavsaini13 SET default_transaction_isolation TO 'read committed';
-- Output: ALTER ROLE

ALTER ROLE arnavsaini13 SET default_transaction_deferrable TO on;
-- Output: ALTER ROLE

ALTER ROLE arnavsaini13 SET timezone TO 'UTC';
-- Output: ALTER ROLE

GRANT ALL PRIVILEGES ON DATABASE bdms_db TO arnavsaini13;
-- Output: GRANT

-- These commands give the user permission to access the database
```

**2.5 Exit PostgreSQL Terminal**
```sql
-- At the postgres=# prompt, type:
\q

-- You'll return to regular PowerShell prompt
-- Database is now ready ✓
```

**Summary of what was created:**
```
Database: bdms_db
User: arnavsaini13
Password: (your chosen password)
```

---

## **STEP 3: Install Python Dependencies** 📦

**What is this?**
- Python libraries/packages that BDMS needs to run
- All listed in `requirements.txt`
- Includes Django, PostgreSQL driver, barcode generator, OCR, etc.

### On Windows (PowerShell):

**3.1 Navigate to Project**
```powershell
# Go to your BDMS project directory
cd "C:\RDSO Internship\BDMS"

# Verify you're in the right place - you should see files like:
# - manage.py
# - requirements.txt
# - BDMS (folder)
# - documents (folder)
# - users (folder)
```

**3.2 Activate Virtual Environment** (if not already active)
```powershell
# If you have a venv folder in BDMS directory:
.\venv\Scripts\Activate.ps1

# You should see (venv) at the start of your prompt:
# (venv) PS C:\RDSO Internship\BDMS>

# If activation fails, create it first:
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**3.3 Install Requirements**
```powershell
# Install all packages listed in requirements.txt
pip install -r requirements.txt

# This will download and install:
# - Django 6.0.5
# - psycopg2-binary (PostgreSQL driver)
# - PyPDF2 (PDF text extraction)
# - python-barcode (Barcode generation)
# - pdf2image (Convert PDF to images)
# - pytesseract (OCR interface)
# - Pillow (Image processing)

# Wait for completion - this takes 2-5 minutes
# You'll see: Successfully installed ... packages
```

**3.4 Verify Installation**
```powershell
# Check if Django is installed correctly
python -c "import django; print(django.get_version())"

# Expected output:
# 6.0.5

# If you see the version, packages are installed correctly ✓
```

---

## **STEP 4: Configure Django Settings** ⚙️

**What is this?**
- Telling Django how to connect to your PostgreSQL database
- Telling Django where Tesseract is located
- This is in the file: `BDMS/settings.py`

### On Windows (Using a Text Editor):

**4.1 Open settings.py**
```powershell
# Using Windows Notepad (easiest for beginners)
notepad "C:\RDSO Internship\BDMS\BDMS\settings.py"

# Or using VS Code (if installed)
code "C:\RDSO Internship\BDMS\BDMS\settings.py"
```

**4.2 Find and Update Database Configuration**

Look for this section (around line 85-95):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bdms_db',
        'USER': 'arnavsaini13',
        'PASSWORD': '',  # ← UPDATE THIS LINE
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Change it to:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bdms_db',
        'USER': 'arnavsaini13',
        'PASSWORD': 'your_secure_password',  # ← Use the password from Step 2.3
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Example (if your password was "MySecurePass123!"):**
```python
'PASSWORD': 'MySecurePass123!',
```

**4.3 Find and Update Tesseract Path**

Look for this section (around line 155-165):

```python
# Tesseract OCR Configuration
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**If your installation path was different:**
- Change the path to match your Tesseract installation location
- Example (if installed in different location):
```python
pytesseract.pytesseract.pytesseract_cmd = r'C:\Your\Custom\Path\Tesseract-OCR\tesseract.exe'
```

**4.4 Save the File**
```
Press: Ctrl + S

Or using File menu: File → Save
```

✓ **Django is now configured to use your database and Tesseract!**

---

## **STEP 5: Run Database Migrations** 🗃️

**What is this?**
- Creates all database tables and structures
- Converts Python model definitions into actual database tables
- Only needs to run once (creates 3 main tables: documents, transactions, users)

### On Windows (PowerShell):

**5.1 Ensure You're in Project Directory**
```powershell
# Navigate to BDMS folder
cd "C:\RDSO Internship\BDMS"

# Verify virtual environment is active (see (venv) at prompt start)
# If not, activate it:
.\venv\Scripts\Activate.ps1
```

**5.2 Create Initial Migrations**
```powershell
# This tells Django to prepare the database structure
python manage.py makemigrations

# Expected output:
# Migrations for 'documents':
#   documents/migrations/0001_initial.py
# Migrations for 'users':
#   users/migrations/0001_initial.py
```

**5.3 Apply Migrations to Database**
```powershell
# This actually creates the tables in PostgreSQL
python manage.py migrate

# Expected output:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, documents, sessions, users
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   Applying auth.0002_alter_user_options... OK
#   ... (many more lines)
#   Applying users.0001_initial... OK

# When complete, you'll see: OK
```

**5.4 Verify Migration Success**
```powershell
# Check if tables were created
python manage.py showmigrations

# Should show all migrations with [X] marks (completed)
# Example:
# admin
#  [X] 0001_initial
#  [X] 0002_logentry_remove_auto_add
# auth
#  [X] 0001_initial
#  [X] 0002_alter_user_options
# ... and many more
```

✓ **Database tables are now created and ready!**

---

## **STEP 6: Create Admin Account** 👤

**What is this?**
- Creates the superuser account
- You use this to login to the admin dashboard
- Has full access to manage everything

### On Windows (PowerShell):

**6.1 Create Superuser**
```powershell
# Make sure you're in the BDMS directory with venv activated
cd "C:\RDSO Internship\BDMS"
.\venv\Scripts\Activate.ps1

# Run the command:
python manage.py createsuperuser

# The system will ask you to enter information:
```

**6.2 Answer the Prompts**

When you run the above command, you'll see:

```
Username: admin
Email address: admin@bdms.gov
Password: 
Password (again):
Superuser created successfully.
```

**Example Input:**
```
Username: admin                    (press Enter after typing)
Email address: admin@example.com   (press Enter after typing)
Password: AdminPassword123!        (type, then press Enter - text won't show)
Password (again): AdminPassword123! (type again, then press Enter)

Output: Superuser created successfully.
```

**Important Notes:**
- Username: Can be anything (e.g., admin, root, superuser)
- Email: Can be any email format (e.g., admin@bdms.gov or admin@example.com)
- Password: Must be at least 8 characters, no spaces
- Password typing: Text won't appear on screen (normal for security)

**Remember these credentials** - you'll use them in Step 7!

✓ **Admin account created!**

---

## **STEP 7: Start the Development Server** 🚀

**What is this?**
- Runs Django development server on your computer
- Makes BDMS accessible at http://localhost:8000
- Only for development (not for production)

### On Windows (PowerShell):

**7.1 Start the Server**
```powershell
# Make sure you're in BDMS directory with venv activated
cd "C:\RDSO Internship\BDMS"
.\venv\Scripts\Activate.ps1

# Start the development server:
python manage.py runserver

# You'll see output like:
```

**Expected Output:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
May 27, 2026 - 12:34:56
Django version 6.0.5, using settings 'BDMS.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**What this means:**
- ✓ Django is running successfully
- ✓ Server is ready to accept connections
- ✓ You can now open http://localhost:8000 in your browser
- To stop the server: Press `Ctrl + C` (or `Ctrl + Break` on some keyboards)

✓ **Server is running!**

---

## **STEP 8: Access the Application** 🌐

**8.1 Open Your Web Browser**

Open any web browser (Chrome, Firefox, Edge, Safari):

```
Type in address bar: http://localhost:8000
Press Enter
```

**You should see:**
- BDMS login page
- Professional government portal interface
- Dark blue header with "BDMS" logo

**8.2 Login with Your Admin Account**

```
Username: admin (or whatever you created)
Password: AdminPassword123! (or your password)
Click Login
```

**After login, you'll see:**
- Dashboard with statistics (0 documents initially)
- Menu options: Upload, Search, Activities, Profile
- User profile dropdown menu

**8.3 Admin Panel (Optional)**

To access the administrative panel:

```
Type in address bar: http://localhost:8000/admin
Press Enter
Login with same credentials

You can now:
- View all documents
- Manage users
- See transaction logs
- Update document status
```

✓ **Application is now running!**

---

## **Troubleshooting Guide** 🔧

### Problem: "psql is not recognized" (Step 2)

**Solution:**
```powershell
# Add PostgreSQL bin to path, then try:
$env:Path += ";C:\Program Files\PostgreSQL\18\bin"
.\psql -U postgres
```

### Problem: "could not connect to database" (Step 5)

**Cause:** Database password in settings.py doesn't match

**Solution:**
1. Check the password you set in Step 2.3
2. Make sure it matches exactly in `BDMS/settings.py` (including case!)
3. No spaces before/after password in settings.py

### Problem: "Tesseract not found" (When uploading scanned PDF)

**Cause:** Path in settings.py is incorrect

**Solution:**
```powershell
# Verify Tesseract is installed:
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version

# If not found, check your actual installation path:
# Windows key → Search "Tesseract"
# Check: C:\Program Files\ for Tesseract folder
# Update the path in BDMS/settings.py accordingly
```

### Problem: Port 8000 already in use

**Cause:** Another application is using port 8000

**Solution:**
```powershell
# Use a different port:
python manage.py runserver 8001

# Then access: http://localhost:8001
```

### Problem: "ModuleNotFoundError" when running server

**Cause:** Dependencies not installed

**Solution:**
```powershell
# Make sure venv is activated (see (venv) at prompt start)
# Then reinstall:
pip install -r requirements.txt
```

---

## **Summary Checklist** ✅

```
[ ] 1. Tesseract OCR installed and verified
    - Checked: "C:\Program Files\Tesseract-OCR\tesseract.exe" --version

[ ] 2. PostgreSQL database created
    - Database name: bdms_db
    - User: arnavsaini13
    - Password: (remembered securely)

[ ] 3. Python dependencies installed
    - Ran: pip install -r requirements.txt
    - All packages installed successfully

[ ] 4. Django configured
    - Updated database password in settings.py
    - Updated Tesseract path in settings.py
    - Saved settings.py

[ ] 5. Database migrations completed
    - Ran: python manage.py makemigrations
    - Ran: python manage.py migrate
    - All migrations marked [X]

[ ] 6. Admin account created
    - Username: admin
    - Email: admin@example.com
    - Password: (remembered securely)

[ ] 7. Development server started
    - Running at http://127.0.0.1:8000/
    - Watching for file changes

[ ] 8. Application accessed and working
    - Logged in successfully
    - Dashboard displaying
    - Admin panel accessible at /admin
```

---

## **What's Next?** 🎯

Now that BDMS is running, you can:

1. **Upload a Document**
   - Click "Upload Document" button
   - Select a PDF file
   - Fill in title, department, category
   - Click upload
   - Barcode automatically generated!

2. **Test Search**
   - Click "Search"
   - Try searching for documents

3. **Check Admin Panel**
   - Visit http://localhost:8000/admin
   - View documents, users, transactions

4. **Create More Users**
   - Click "Sign Up" on login page
   - Create regular user accounts
   - Test different roles

---

## **Helpful Links** 📖

- Django Documentation: https://docs.djangoproject.com/en/6.0/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Bootstrap (Frontend): https://getbootstrap.com/docs/5.3/
- Python Documentation: https://docs.python.org/3/

---

## **Getting Help** 💬

If you encounter issues:

1. Check the **Troubleshooting Guide** above
2. Read the **README.md** in the BDMS folder
3. Check Django error messages (usually very descriptive)
4. Verify file paths are correct (Windows is case-insensitive but be careful)

---

**Congratulations! Your BDMS system is now ready to use!** 🎉
