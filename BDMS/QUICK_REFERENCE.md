# BDMS Quick Reference Sheet - Copy & Paste Commands

## 🚀 Quick Start Commands

### Step 1: Verify Tesseract (After Installation)
```powershell
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```
✓ If you see version info, Tesseract is installed

---

### Step 2: Create PostgreSQL Database
```powershell
# Open PostgreSQL terminal
cd "C:\Program Files\PostgreSQL\18\bin"
.\psql -U postgres

# Then in PostgreSQL terminal, paste these one by one:
```

**Copy-Paste for PostgreSQL Terminal:**
```sql
CREATE DATABASE bdms_db;
CREATE USER arnavsaini13 WITH PASSWORD 'your_secure_password';
ALTER ROLE arnavsaini13 SET client_encoding TO 'utf8';
ALTER ROLE arnavsaini13 SET default_transaction_isolation TO 'read committed';
ALTER ROLE arnavsaini13 SET default_transaction_deferrable TO on;
ALTER ROLE arnavsaini13 SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE bdms_db TO arnavsaini13;
\q
```

**Important:** Replace `'your_secure_password'` with your actual password
Example: `'MySecurePass123!'`

---

### Step 3: Install Python Dependencies
```powershell
# Navigate to BDMS directory
cd "C:\RDSO Internship\BDMS"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install all packages
pip install -r requirements.txt

# Verify Django
python -c "import django; print(django.get_version())"
```

---

### Step 4: Configure Django Settings

**Open file:** `C:\RDSO Internship\BDMS\BDMS\settings.py`

**Find (around line 85-95) and update:**
```python
# OLD VERSION:
'PASSWORD': '',

# NEW VERSION:
'PASSWORD': 'your_secure_password',
```

**Example:**
```python
'PASSWORD': 'MySecurePass123!',
```

**Also check (around line 155-165):**
```python
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Save file:** `Ctrl + S`

---

### Step 5: Run Migrations
```powershell
# Make sure venv is active (you should see (venv) at prompt)
cd "C:\RDSO Internship\BDMS"
.\venv\Scripts\Activate.ps1

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Verify
python manage.py showmigrations
```

✓ All migrations should show [X] mark

---

### Step 6: Create Admin Account
```powershell
# Make sure venv is active
cd "C:\RDSO Internship\BDMS"
.\venv\Scripts\Activate.ps1

# Create superuser
python manage.py createsuperuser

# When prompted, enter:
# Username: admin
# Email: admin@example.com
# Password: YourPassword123! (type it twice when asked)
```

**Important:** Remember your username and password!

---

### Step 7: Start Development Server
```powershell
# Make sure venv is active
cd "C:\RDSO Internship\BDMS"
.\venv\Scripts\Activate.ps1

# Start server
python manage.py runserver

# You should see:
# Starting development server at http://127.0.0.1:8000/
# To stop, press Ctrl+C
```

---

### Step 8: Access Application
```
Open your browser and go to: http://localhost:8000

Login with:
Username: admin
Password: (whatever you created)

Admin panel: http://localhost:8000/admin
```

---

## 📝 Important File Locations

| File | Location | Purpose |
|------|----------|---------|
| settings.py | `C:\RDSO Internship\BDMS\BDMS\settings.py` | Django config (DB password, Tesseract path) |
| manage.py | `C:\RDSO Internship\BDMS\manage.py` | Django commands |
| requirements.txt | `C:\RDSO Internship\BDMS\requirements.txt` | Python packages list |
| README.md | `C:\RDSO Internship\BDMS\README.md` | Full documentation |

---

## ⚠️ Common Mistakes

### ❌ Mistake 1: Database password doesn't match
**Fix:** Check that the password in `settings.py` exactly matches what you set in PostgreSQL

### ❌ Mistake 2: Virtual environment not activated
**Fix:** Look for `(venv)` at start of PowerShell prompt
If missing: Run `.\venv\Scripts\Activate.ps1`

### ❌ Mistake 3: Tesseract path wrong
**Fix:** Verify with: `"C:\Program Files\Tesseract-OCR\tesseract.exe" --version`
Update path in `settings.py` if installed elsewhere

### ❌ Mistake 4: Port 8000 already in use
**Fix:** Use different port: `python manage.py runserver 8001`

### ❌ Mistake 5: Forgot password during setup
**Fix:** Can't recover, must:
1. Delete database: `DROP DATABASE bdms_db;`
2. Delete user: `DROP USER arnavsaini13;`
3. Start over from Step 2

---

## 🆘 Emergency Commands

**Reset Everything (if something breaks):**
```powershell
# Stop the server first (Ctrl+C)

# Delete database
cd "C:\Program Files\PostgreSQL\18\bin"
.\psql -U postgres
DROP DATABASE bdms_db;
DROP USER arnavsaini13;
\q

# Start over from Step 2
```

**Clear Python Cache:**
```powershell
# If you see weird Python errors
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

**Reinstall Python Packages:**
```powershell
cd "C:\RDSO Internship\BDMS"
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## ✅ Verification Checklist

After each step, check:

```
Step 1 ✓ Tesseract: "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
         (Should show: tesseract 5.x.x)

Step 2 ✓ PostgreSQL: psql -U arnavsaini13 -d bdms_db -c "SELECT 1;"
         (Should show: 1)

Step 3 ✓ Django: python -c "import django; print(django.get_version())"
         (Should show: 6.0.5)

Step 5 ✓ Migrations: python manage.py showmigrations
         (All should have [X])

Step 6 ✓ Superuser: python manage.py shell
         > from django.contrib.auth.models import User
         > User.objects.filter(username='admin').exists()
         > (Should return: True)

Step 7 ✓ Server: http://127.0.0.1:8000/
         (Should load login page)

Step 8 ✓ Login: Try admin/password
         (Should see dashboard)
```

---

## 📞 If Something Goes Wrong

### Error: "could not connect to server"
```powershell
# PostgreSQL not running?
# Try:
pg_isready -h localhost -p 5432

# If fails, restart PostgreSQL service
# Windows Start Menu → Services → postgresql-x64-18 → Restart
```

### Error: "ModuleNotFoundError"
```powershell
# Venv not activated or packages missing
# Verify venv active (see (venv) at prompt)
# If not: .\venv\Scripts\Activate.ps1
# Reinstall: pip install -r requirements.txt
```

### Error: "Port 8000 already in use"
```powershell
# Use different port:
python manage.py runserver 8001
# Access at: http://localhost:8001
```

### Error: "Invalid syntax" in settings.py
```
Check these common mistakes:
- Extra or missing quotes
- Missing colons at end of lines
- Wrong indentation
- Special characters without quotes

Compare with the example in SETUP_GUIDE_DETAILED.md
```

---

## 💡 Pro Tips

1. **Keep terminal open during development**
   - Server logs show errors and requests
   - Helps debug issues

2. **Use Ctrl+C to stop server, not just close window**
   - Allows clean shutdown
   - Helps when restarting

3. **Browser developer tools (F12) show frontend errors**
   - Useful for JavaScript/CSS issues

4. **Django admin is your friend**
   - http://localhost:8000/admin
   - Manage documents, users, transactions from here

5. **Don't share your password**
   - In settings.py or anywhere
   - It's for your database only

---

## 📚 Next Steps After Setup

1. **Upload your first document:**
   - Click "Upload Document"
   - Select a PDF
   - Watch barcode auto-generate!

2. **Create test user:**
   - Click "Sign Up"
   - Create regular user account
   - Test different permissions

3. **Try admin features:**
   - Go to /admin
   - Update document status
   - View transaction logs

4. **Explore search:**
   - Upload multiple PDFs
   - Test search by barcode/title/content
   - Try filters

---

## 🎯 Success Indicators

You'll know everything is working when:

✅ Tesseract installed and verified
✅ PostgreSQL database created with user
✅ Python packages installed (pip list shows 8+ packages)
✅ Django configured with database password
✅ Migrations completed (all marked [X])
✅ Admin account created
✅ Server running at http://localhost:8000
✅ Can login with admin credentials
✅ Dashboard loads with 0 documents
✅ Can upload a PDF and see barcode generated
✅ Barcode stored in media/ folder

---

**You're ready to go! 🚀**

If stuck, refer to SETUP_GUIDE_DETAILED.md for full explanations.
