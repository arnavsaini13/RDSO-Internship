param(
    [string]$ServiceName = 'postgresql-x64-18',
    [string]$DataDir = 'C:\Program Files\PostgreSQL\18\data',
    [string]$Username,
    [switch]$AllowCreatedb
)

$ErrorActionPreference = 'Stop'

function Assert-Administrator {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'Run this script in an elevated PowerShell session (Run as Administrator).'
    }
}

function ConvertTo-PlainText {
    param([Security.SecureString]$SecureString)
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureString)
    try {
        [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        if ($bstr -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
    }
}

function Escape-SqlLiteral {
    param([string]$Value)
    $Value.Replace("'", "''")
}

function Escape-SqlIdentifier {
    param([string]$Value)
    $Value.Replace('"', '""')
}

Assert-Administrator

if (-not $Username) {
    $Username = Read-Host 'New PostgreSQL username'
}

if ([string]::IsNullOrWhiteSpace($Username)) {
    throw 'Username cannot be empty.'
}

$securePassword = Read-Host "Password for $Username" -AsSecureString
$plainPassword = ConvertTo-PlainText -SecureString $securePassword
$sqlUsername = Escape-SqlIdentifier -Value $Username
$sqlPassword = Escape-SqlLiteral -Value $plainPassword
$createdbClause = if ($AllowCreatedb) { ' CREATEDB' } else { '' }

$pgHbaPath = Join-Path $DataDir 'pg_hba.conf'
$backupPath = "$pgHbaPath.bak"
$originalContent = Get-Content -Path $pgHbaPath -Raw

try {
    if (-not (Test-Path $backupPath)) {
        Set-Content -Path $backupPath -Value $originalContent -NoNewline
    }

    $trustedContent = $originalContent `
        -replace 'local\s+all\s+all\s+scram-sha-256', 'local   all             all                                     trust' `
        -replace 'host\s+all\s+all\s+127\.0\.0\.1/32\s+scram-sha-256', 'host    all             all             127.0.0.1/32            trust' `
        -replace 'host\s+all\s+all\s+::1/128\s+scram-sha-256', 'host    all             all             ::1/128                 trust' `
        -replace 'local\s+replication\s+all\s+scram-sha-256', 'local   replication     all                                     trust' `
        -replace 'host\s+replication\s+all\s+127\.0\.0\.1/32\s+scram-sha-256', 'host    replication     all             127.0.0.1/32            trust' `
        -replace 'host\s+replication\s+all\s+::1/128\s+scram-sha-256', 'host    replication     all             ::1/128                 trust'

    Set-Content -Path $pgHbaPath -Value $trustedContent -NoNewline
    Restart-Service -Name $ServiceName

    $checkSql = "SELECT 1 FROM pg_roles WHERE rolname = '$sqlUsername';"
    $existingRole = & 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -U postgres -h 127.0.0.1 -d postgres -tAc $checkSql
    if ([string]::IsNullOrWhiteSpace($existingRole)) {
        $existingRole = '0'
    }
    else {
        $existingRole = $existingRole.Trim()
    }

    if ($existingRole -eq '1') {
        $roleSql = "ALTER ROLE `"$sqlUsername`" WITH LOGIN PASSWORD '$sqlPassword'$createdbClause;"
    }
    else {
        $roleSql = "CREATE ROLE `"$sqlUsername`" WITH LOGIN PASSWORD '$sqlPassword'$createdbClause;"
    }

    $roleSqlFile = Join-Path $env:TEMP 'create-postgres-user.sql'
    Set-Content -Path $roleSqlFile -Value $roleSql -NoNewline
    & 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -U postgres -h 127.0.0.1 -d postgres -v ON_ERROR_STOP=1 -f $roleSqlFile

    $env:PGPASSWORD = $plainPassword
    try {
        & 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -U $Username -h 127.0.0.1 -d postgres -c 'SELECT current_user;'
    }
    finally {
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    }

    Write-Host "Done. Username: $Username"
}
finally {
    Set-Content -Path $pgHbaPath -Value $originalContent -NoNewline
    Restart-Service -Name $ServiceName
}