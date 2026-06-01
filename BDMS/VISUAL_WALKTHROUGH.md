# BDMS Setup - Visual Walkthrough Guide

## 🎬 What You'll See At Each Step

This guide describes exactly what should appear on your screen at each step.

---

## **STEP 1: Install Tesseract - Visual Walkthrough**

### 1.1 After Downloading the Installer

**You'll see:**
- A file named: `tesseract-ocr-w64-setup-v5.3.exe` (or similar)
- File size: ~250 MB
- Location: Your Downloads folder

### 1.2 Double-Click the Installer

**You'll see:**
```
┌─────────────────────────────────────────┐
│  Tesseract-OCR Setup Wizard             │
│                                         │
│  Welcome to Tesseract OCR               │
│  Version 5.3.0                          │
│                                         │
│  [Next >]  [Cancel]                     │
└─────────────────────────────────────────┘
```

**Click:** `[Next >]`

### 1.3 License Agreement

**You'll see:**
```
┌─────────────────────────────────────────┐
│  License Agreement                      │
│                                         │
│  [Scrollable text of license]           │
│                                         │
│  ☐ I Agree to the License               │
│                                         │
│  [< Back]  [Next >]  [Cancel]           │
└─────────────────────────────────────────┘
```

**Click:** Checkbox next to "I Agree"
**Then click:** `[Next >]`

### 1.4 Installation Path

**You'll see:**
```
┌─────────────────────────────────────────┐
│  Choose Installation Location           │
│                                         │
│  Install to:                            │
│  C:\Program Files\Tesseract-OCR         │
│  [Browse...]                            │
│                                         │
│  [< Back]  [Next >]  [Cancel]           │
└─────────────────────────────────────────┘
```

**Don't change anything** - keep default path
**Click:** `[Next >]`

### 1.5 Installation

**You'll see:**
```
┌─────────────────────────────────────────┐
│  Installing...                          │
│                                         │
│  ████████████████░░░░░░░░░░░░░░░░░░░░░░│
│  45% Complete - Installing files        │
│                                         │
│  Time remaining: ~2 minutes             │
└─────────────────────────────────────────┘
```

**Wait** for installation to complete (2-3 minutes)

### 1.6 Installation Complete

**You'll see:**
```
┌─────────────────────────────────────────┐
│  Installation Complete!                 │
│                                         │
│  Tesseract OCR has been installed       │
│  successfully to:                       │
│  C:\Program Files\Tesseract-OCR         │
│                                         │
│  [Finish]                               │
└─────────────────────────────────────────┘
```

**Click:** `[Finish]`

### 1.7 Verify Installation (PowerShell)

**Open PowerShell** (Right-click Start → Windows PowerShell (Admin))

**Type this command:**
```powershell
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

**You should see:**
```
tesseract 5.3.0
leptonica-1.82.0
libjpeg 6b (libjpeg-turbo 2.1.0)
libpng 1.6.37
libtiff 4.3.0
zlib 1.2.11
...
```

✅ **If you see version info - Tesseract is installed!**

---

## **STEP 2: PostgreSQL Database - Visual Walkthrough**

### 2.1 Open PostgreSQL Terminal

**In PowerShell, type:**
```powershell
cd "C:\Program Files\PostgreSQL\18\bin"
.\psql -U postgres
```

**You'll be prompted:**
```
Password for user postgres:
```

**Enter:** Your PostgreSQL admin password (created during PostgreSQL installation)

**You should see:**
```
psql (18.0)
Type "help" for help.

postgres=#
```

✅ **Now you're connected to PostgreSQL!**

### 2.2 Create Database

**At the `postgres=#` prompt, type:**
```sql
CREATE DATABASE bdms_db;
```

**Press Enter**

**You should see:**
```
CREATE DATABASE
postgres=#
```

✅ **Database created!**

### 2.3 Create User

**Type:**
```sql
CREATE USER arnavsaini13 WITH PASSWORD 'your_secure_password';
```

**Replace:** `'your_secure_password'` with your actual password
**Example:** `'MySecurePass123!'`

**Press Enter**

**You should see:**
```
CREATE ROLE
postgres=#
```

✅ **User created!**

### 2.4 Grant Privileges

**Type these commands one by one (press Enter after each):**

```sql
ALTER ROLE arnavsaini13 SET client_encoding TO 'utf8';
```
**Response:** `ALTER ROLE`

```sql
ALTER ROLE arnavsaini13 SET default_transaction_isolation TO 'read committed';
```
**Response:** `ALTER ROLE`

```sql
ALTER ROLE arnavsaini13 SET default_transaction_deferrable TO on;
```
**Response:** `ALTER ROLE`

```sql
ALTER ROLE arnavsaini13 SET timezone TO 'UTC';
```
**Response:** `ALTER ROLE`

```sql
GRANT ALL PRIVILEGES ON DATABASE bdms_db TO arnavsaini13;
```
**Response:** `GRANT`

### 2.5 Exit PostgreSQL

**Type:**
```sql
\q
```

**You should return to PowerShell:**
```
PS C:\Program Files\PostgreSQL\18\bin>
```

✅ **Database setup complete!**

---

## **STEP 3: Install Python Packages - Visual Walkthrough**

### 3.1 Navigate to BDMS

**In PowerShell, type:**
```powershell
cd "C:\RDSO Internship\BDMS"
```

**You should see:**
```
PS C:\RDSO Internship\BDMS>
```

### 3.2 Activate Virtual Environment

**Type:**
```powershell
.\venv\Scripts\Activate.ps1
```

**You should see:**
```
(venv) PS C:\RDSO Internship\BDMS>
```

✅ **Notice the `(venv)` at the start - that means it's active!**

### 3.3 Install Requirements

**Type:**
```powershell
pip install -r requirements.txt
```

**You'll see a long list of packages being installed:**
```
Collecting Django==6.0.5
  Downloading Django-6.0.5-py3-none-any.whl (8.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 8.1/8.1 MB
Collecting psycopg2-binary==2.9.11
  Downloading psycopg2_binary-2.9.11-cp313-cp313-win_amd64.whl (2.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 2.9/2.9 MB
...
Successfully installed Django-6.0.5 psycopg2-binary-2.9.11 PyPDF2-4.1.1 ...
```

**Wait for all packages to install** (takes 2-5 minutes)

**Final message:**
```
Successfully installed Django-6.0.5 psycopg2-binary-2.9.11 PyPDF2-4.1.1 
python-barcode-0.15.1 pdf2image-1.17.1 pytesseract-0.3.13 Pillow-10.1.0 
Werkzeug-3.0.1

(venv) PS C:\RDSO Internship\BDMS>
```

✅ **All packages installed!**

---

## **STEP 4: Configure Django - Visual Walkthrough**

### 4.1 Open settings.py

**In PowerShell, type:**
```powershell
notepad "BDMS\settings.py"
```

**Notepad opens with the file**

### 4.2 Find Database Section

**Use keyboard shortcut:** `Ctrl + F` (opens Find dialog)

**Search for:** `PASSWORD`

**You'll see:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bdms_db',
        'USER': 'arnavsaini13',
        'PASSWORD': '',  # ← This is empty, we need to fill it
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4.3 Update Password

**Change from:**
```python
'PASSWORD': '',
```

**To:**
```python
'PASSWORD': 'MySecurePass123!',
```

✅ **Use the same password from Step 2.3!**

### 4.4 Find and Verify Tesseract Path

**Use:** `Ctrl + F` → Search for `pytesseract_cmd`

**You'll see:**
```python
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

✅ **This should already be correct (matches Tesseract installation path)**

### 4.5 Save File

**Press:** `Ctrl + S`

**Or use menu:** `File → Save`

**Close the file**

✅ **Django configured!**

---

## **STEP 5: Run Migrations - Visual Walkthrough**

### 5.1 Make Migrations

**In PowerShell (with venv active), type:**
```powershell
python manage.py makemigrations
```

**You should see:**
```
Migrations for 'documents':
  documents/migrations/0001_initial.py
    - Create model Document
    - Create model Transaction
    - Create model UserProfile
Migrations for 'users':
  users/migrations/0001_initial.py
    - Create model UserProfile

(venv) PS C:\RDSO Internship\BDMS>
```

✅ **Migration files created!**

### 5.2 Apply Migrations

**Type:**
```powershell
python manage.py migrate
```

**You'll see:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, documents, sessions, users
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying auth.0002_alter_user_options... OK
  Applying auth.0003_alter_user_email_max_length... OK
  ... (many more OK messages)
  Applying documents.0001_initial... OK
  Applying users.0001_initial... OK

(venv) PS C:\RDSO Internship\BDMS>
```

✅ **All migrations applied!**

### 5.3 Verify Migrations

**Type:**
```powershell
python manage.py showmigrations
```

**You should see:**
```
admin
 [X] 0001_initial
 [X] 0002_logentry_remove_auto_add
auth
 [X] 0001_initial
 [X] 0002_alter_user_options
 ... (many more with [X])
documents
 [X] 0001_initial
users
 [X] 0001_initial

(venv) PS C:\RDSO Internship\BDMS>
```

✅ **All marked [X] - database is ready!**

---

## **STEP 6: Create Admin Account - Visual Walkthrough**

### 6.1 Run Command

**Type:**
```powershell
python manage.py createsuperuser
```

**System prompts you:**
```
Username:
```

### 6.2 Enter Username

**Type:** `admin`

**Press Enter**

```
Email address:
```

### 6.3 Enter Email

**Type:** `admin@example.com` (or any email format)

**Press Enter**

```
Password:
```

### 6.4 Enter Password

**Type:** Your password (text WON'T show as you type - that's normal!)

**Example:** Type `AdminPassword123!` then Press Enter

```
Password (again):
```

### 6.5 Confirm Password

**Type the same password again**

**Press Enter**

**You should see:**
```
Superuser created successfully.

(venv) PS C:\RDSO Internship\BDMS>
```

✅ **Admin account created!**

### 6.6 What You Just Created

```
Username: admin
Email: admin@example.com
Password: AdminPassword123! (whatever you entered)
Role: Superuser (full access)
```

---

## **STEP 7: Start Server - Visual Walkthrough**

### 7.1 Run Development Server

**Type:**
```powershell
python manage.py runserver
```

**You'll see:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
May 27, 2026 - 12:34:56
Django version 6.0.5, using settings 'BDMS.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

✅ **Server is running!**

### 7.2 Keep Terminal Open

**Important:** Leave this PowerShell window open and running!

**This terminal will:**
- Show you any errors
- Show you when pages are accessed
- Display debug information

**Example output when you load a page:**
```
[27/May/2026 12:35:10] "GET / HTTP/1.1" 301 0
[27/May/2026 12:35:10] "GET /auth/login/ HTTP/1.1" 200 5234
```

✅ **Server terminal should stay running during development**

---

## **STEP 8: Access Application - Visual Walkthrough**

### 8.1 Open Browser

**Open any web browser** (Chrome, Firefox, Edge, Safari)

### 8.2 Navigate to Application

**In address bar, type:**
```
http://localhost:8000
```

**Press Enter**

**You should see:**
```
┌────────────────────────────────────────────────────────┐
│  BDMS                                  [User Dropdown]  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Login                                                 │
│                                                        │
│  Username: [___________________]                       │
│  Password: [___________________]                       │
│                                                        │
│  [Login Button]                                        │
│                                                        │
│  Don't have account? [Sign Up Here]                    │
│                                                        │
│                                                        │
│  📋 Secure Government Portal                          │
└────────────────────────────────────────────────────────┘
```

✅ **Login page loaded!**

### 8.3 Login

**Username field:** Type `admin`

**Password field:** Type your password

**Click:** `[Login Button]`

### 8.4 After Login

**You should see the Dashboard:**
```
┌────────────────────────────────────────────────────────┐
│  BDMS                                  [User Dropdown]  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Dashboard                                             │
│  Welcome, admin! Here's your system overview.           │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Total    │  │ Your     │  │ Pending  │              │
│  │Documents │  │ Uploads  │  │Documents │              │
│  │    0     │  │    0     │  │    0     │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                        │
│  [Recent Uploads]  [Recent Activities]                 │
│  No documents uploaded yet                             │
│                                                        │
│  [Upload Document] [Search] [Activities] [Profile]     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

✅ **Dashboard loaded - Everything works!**

### 8.5 Admin Panel (Optional)

**In address bar, type:**
```
http://localhost:8000/admin
```

**Press Enter**

**You should see Admin Login:**
```
┌────────────────────────────────────────────────────────┐
│                  Django Administration                │
│                                                        │
│  Username: [___________________]                       │
│  Password: [___________________]                       │
│                                                        │
│  [Log in]                                              │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Use same credentials:** admin / your_password

**After login, you see:**
```
┌────────────────────────────────────────────────────────┐
│  Django Administration                                 │
│                                                        │
│  Site administration                                   │
│                                                        │
│  ▸ DOCUMENTS                                           │
│    • Documents                                         │
│    • Transactions                                      │
│    • User Profiles                                     │
│                                                        │
│  ▸ AUTHENTICATION AND AUTHORIZATION                    │
│    • Users                                             │
│    • Groups                                            │
│                                                        │
│  [Logout]                                              │
│                                                        │
└────────────────────────────────────────────────────────┘
```

✅ **Admin panel working!**

---

## **🎉 Congratulations!**

If you've seen all these screens and they match the descriptions, your BDMS system is **fully installed and working!**

### What You've Accomplished:
```
✅ Installed Tesseract OCR
✅ Created PostgreSQL Database
✅ Installed Python Packages
✅ Configured Django
✅ Created Database Tables
✅ Created Admin Account
✅ Started Development Server
✅ Accessed the Application
✅ Logged in Successfully
```

### What's Next?
1. **Try uploading a document** - Click "Upload Document"
2. **Test barcode generation** - Select a PDF and watch the magic happen!
3. **Try search** - Upload multiple documents and search them
4. **Explore admin panel** - Manage documents and users

---

## ⚠️ If You See Different Screens

### "Connection Refused" Error
```
This site can't be reached
127.0.0.1:8000 took too long to respond
```
**Fix:** Check PowerShell terminal - is server still running?
- Restart with: `python manage.py runserver`

### "Page Not Found" (404)
```
Page not found (404)
Request Method: GET
Request URL: http://localhost:8000/something/
```
**Fix:** Make sure you're at `http://localhost:8000` (not a wrong URL)

### "Permission Denied" on Login
```
Invalid username or password
```
**Fix:** Check you typed correct username/password
- Username: admin (what you created in Step 6)
- Password: (what you set in Step 6)

### "Database Connection Error"
```
Error connecting to database
```
**Fix:** Check settings.py password matches PostgreSQL password from Step 2

---

**You're all set! Enjoy using BDMS!** 🚀
