<#
.SYNOPSIS
  Trình khởi chạy 2Anh Studio (bản Việt mở rộng của PPT Master): cài đặt, kiểm tra, cập nhật, cài công cụ tuỳ chọn.
.PARAMETER Action
  setup  - kiểm tra Python, cài thư viện, tạo .env, công cụ tuỳ chọn, chạy doctor
  check  - chạy doctor
  update - cập nhật bằng git (update_repo.py của upstream) rồi kiểm tra nhanh
  tool   - cài công cụ tuỳ chọn cho tài khoản hiện tại (dùng với -Name), in JSON
.PARAMETER Auto
  Dùng với setup: tự cài không hỏi (Python cho tài khoản, venv, thư viện, .env), in một đối tượng JSON ra stdout.
.PARAMETER PlanOnly
  Dùng với setup -Auto hoặc tool: chỉ in kế hoạch dạng JSON; không tải, không cài, không tạo file.
.PARAMETER Name
  Dùng với tool: ffmpeg hoặc pandoc. Tên khác in lỗi JSON và thoát mã 1.
.PARAMETER NonInteractive
  Không hỏi Y/N và không tự cài phần mềm (dùng khi kiểm thử).
#>
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('setup', 'check', 'update', 'tool')]
    [string]$Action,
    [switch]$Auto,
    [switch]$PlanOnly,
    [string]$Name,
    [switch]$NonInteractive
)

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false } catch { }
$env:PYTHONIOENCODING = 'utf-8'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Doctor = Join-Path $RepoRoot 'tools\vi\doctor.py'
$FixDoc = Join-Path $RepoRoot 'docs\vi\xu-ly-loi.md'
$InstallDoc = Join-Path $RepoRoot 'docs\vi\cai-dat-windows.md'
$VenvDir = Join-Path $RepoRoot 'venv'
$VenvPython = Join-Path $VenvDir 'Scripts\python.exe'
$MaxRepoPathLength = 80

# Bộ cài python.org dự phòng khi không có winget. Đổi phiên bản: xem docs/vi/phat-trien/bao-tri.md.
$PythonVersion = '3.12.10'
$PythonInstallers = @{
    amd64 = @{ Url = 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe'; Sha256 = '67B5635E80EA51072B87941312D00EC8927C4DB9BA18938F7AD2D27B328B95FB' }
    arm64 = @{ Url = 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-arm64.exe'; Sha256 = '377AC8FD478987940088E879441E702A71B53164D2A1E6F1D51FF77A7E470258' }
}
$OptionalTools = @{
    ffmpeg = @{ Id = 'Gyan.FFmpeg'; Exe = 'ffmpeg.exe'; Manual = 'https://ffmpeg.org/download.html' }
    pandoc = @{ Id = 'JohnMacFarlane.Pandoc'; Exe = 'pandoc.exe'; Manual = 'https://pandoc.org/installing.html' }
    chromium = @{ Id = $null; Exe = $null; Manual = 'https://playwright.dev/python/docs/browsers' }
}
$script:SetupError = $null

function Write-Step([string]$Text) { Write-Host ''; Write-Host "==> $Text" -ForegroundColor Cyan }
function Write-Fail([string]$Text) { Write-Host "[LỖI] $Text" -ForegroundColor Red }
function Write-Ok([string]$Text) { Write-Host "[OK] $Text" -ForegroundColor Green }

# Chế độ cho AI (setup -Auto, -PlanOnly, tool): stdout chỉ có một dòng JSON, mọi dòng khác ra stderr.
function Write-Log([string]$Text) { [Console]::Error.WriteLine($Text) }
function Write-Json($Object) { [Console]::Out.WriteLine(($Object | ConvertTo-Json -Depth 6 -Compress)) }
function Invoke-Logged([scriptblock]$Command) { & $Command 2>&1 | ForEach-Object { Write-Log "$_" } }
function Set-SetupError([string]$Step, [string]$Message, [string]$Fix) {
    $script:SetupError = [pscustomobject]@{ step = $Step; message = $Message; fix = $Fix }
}

function Test-Winget { return [bool](Get-Command winget -ErrorAction SilentlyContinue) }

function Confirm-Choice([string]$Question) {
    if ($NonInteractive) { return $false }
    $answer = Read-Host "$Question (Y/N)"
    return ($answer -match '^(y|yes|c|co|có)$')
}

function Get-PythonInfo {
    $cmd = Get-Command python -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $cmd) { return $null }
    $version = $null
    try {
        $raw = & $cmd.Source -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and $raw) { $version = [version]("$raw".Trim()) }
    } catch { $version = $null }
    return [pscustomobject]@{
        Path         = $cmd.Source
        Version      = $version
        IsStoreAlias = ($cmd.Source -like '*\WindowsApps\*')
    }
}

function Get-LauncherPython {
    $launcher = Get-Command py -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $launcher) { return $null }
    try {
        $raw = @(& $launcher.Source -3 -c "import sys; print(sys.executable); print('%d.%d' % sys.version_info[:2])" 2>$null)
        if ($LASTEXITCODE -ne 0 -or $raw.Count -lt 2) { return $null }
        $version = [version]("$($raw[$raw.Count - 1])".Trim())
    } catch { return $null }
    if ($version -lt [version]'3.10') { return $null }
    return [pscustomobject]@{
        Path    = "$($raw[$raw.Count - 2])".Trim()
        Version = $version
    }
}

function Get-UserPythonPath {
    if (-not $env:LOCALAPPDATA) { return $null }
    foreach ($folder in 'Python312', 'Python312-arm64') {
        $candidate = Join-Path $env:LOCALAPPDATA "Programs\Python\$folder\python.exe"
        if (Test-Path $candidate) { return $candidate }
    }
    return $null
}

function Find-BasePython {
    $py = Get-PythonInfo
    if ($py -and $py.Version -and $py.Version -ge [version]'3.10') { return $py.Path }
    $launcher = Get-LauncherPython
    if ($launcher) { return $launcher.Path }
    return (Get-UserPythonPath)
}

function Resolve-Python([bool]$OfferInstall) {
    $py = Get-PythonInfo
    if ($py -and $py.Version -and $py.Version -ge [version]'3.10') {
        Write-Ok "Python $($py.Version) tại $($py.Path)"
        return $py
    }
    $installed = Get-LauncherPython
    if ($installed) {
        Write-Fail "Đã cài Python $($installed.Version) tại $($installed.Path) nhưng bản này chưa có trong PATH."
        Write-Host 'Cách sửa: Settings → Apps → Installed apps → Python 3.x → Modify → tick "Add Python to environment variables" (hoặc chạy lại bộ cài tải từ python.org và chọn Modify).'
        Write-Host 'Sau đó đóng cửa sổ này, mở lại rồi bấm lại CAI-DAT.bat.'
        Write-Host "Hướng dẫn chi tiết: $FixDoc (mục Đã cài Python nhưng bộ cài báo không tìm thấy)"
        return $null
    }
    if (-not $py) {
        Write-Fail 'Chưa tìm thấy Python trong PATH.'
    } elseif ((-not $py.Version) -and $py.IsStoreAlias) {
        Write-Fail 'Lệnh python đang trỏ tới lối tắt của Microsoft Store, chưa phải Python thật.'
        Write-Host 'Tắt lối tắt: Settings → Apps → Advanced app settings → App execution aliases → tắt "python.exe" và "python3.exe".'
    } elseif (-not $py.Version) {
        Write-Fail "Không chạy được Python tại $($py.Path)."
    } else {
        Write-Fail "Python $($py.Version) quá cũ, cần 3.10 trở lên."
    }
    if ($OfferInstall -and (Test-Winget) -and (Confirm-Choice 'Cài Python 3.12 bằng winget?')) {
        winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements | Out-Host
        Write-Host ''
        Write-Host 'Đã chạy trình cài Python. Hãy ĐÓNG cửa sổ này rồi bấm lại CAI-DAT.bat để PATH mới có hiệu lực.' -ForegroundColor Yellow
    } else {
        Write-Host 'Cài Python 3.12 tại https://www.python.org/downloads/ và tick "Add python.exe to PATH".'
        Write-Host "Hướng dẫn chi tiết: $InstallDoc"
    }
    return $null
}

function Resolve-RunPython([bool]$OfferInstall = $false) {
    if (Test-Path $VenvPython) {
        if (-not (Test-VenvPython @('-c', 'import sys'))) {
            Write-Fail 'Môi trường venv bị hỏng hoặc tạo dở.'
            Write-Host 'Cách sửa: xoá thư mục venv trong bộ công cụ rồi bấm lại CAI-DAT.bat (hoặc nhờ AI chạy lại lệnh cài).'
            return $null
        }
        Write-Ok "Python của venv tại $VenvPython"
        return [pscustomobject]@{ Path = $VenvPython }
    }
    return (Resolve-Python $OfferInstall)
}

function Invoke-Doctor($Py, [string[]]$DoctorArgs) {
    & $Py.Path $Doctor @DoctorArgs | Out-Host
    return $LASTEXITCODE
}

function Invoke-Setup {
    Write-Step 'Bước 1/4: Kiểm tra Python'
    $py = Resolve-RunPython $true
    if (-not $py) { return 1 }

    Write-Step 'Bước 2/4: Cài thư viện Python (lần đầu có thể mất vài phút)'
    & $py.Path -m pip install --upgrade pip | Out-Host
    & $py.Path -m pip install -r (Join-Path $RepoRoot 'requirements.txt') | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Fail 'Cài thư viện thất bại. Xem thông báo phía trên.'
        Write-Host "Cách xử lý: $FixDoc (mục Cài thư viện thất bại)"
        return 1
    }
    & $py.Path -m pip install -r (Join-Path $RepoRoot 'tools\vi\requirements-vi.txt') | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Host '[CẢNH BÁO] Chưa cài được python-docx (thư viện soạn đề). Tạo slide vẫn dùng bình thường; khi cần soạn đề, bấm đúp lại CAI-DAT.bat.' -ForegroundColor Yellow
    }
    Write-Ok 'Đã cài thư viện.'

    Write-Step 'Bước 3/4: Tạo file cấu hình .env'
    $envFile = Join-Path $RepoRoot '.env'
    if (Test-Path $envFile) {
        Write-Ok 'Đã có .env, giữ nguyên.'
    } else {
        Copy-Item (Join-Path $RepoRoot '.env.example') $envFile
        Write-Ok 'Đã tạo .env từ .env.example.'
    }

    Write-Step 'Bước 4/4: Công cụ tuỳ chọn'
    $optional = @(
        @{ Command = 'git'; Id = 'Git.Git'; Label = 'Git (để cập nhật bằng CAP-NHAT.bat)' },
        @{ Command = 'pandoc'; Id = 'JohnMacFarlane.Pandoc'; Label = 'Pandoc (chuyển tài liệu định dạng cũ)' },
        @{ Command = 'ffmpeg'; Id = 'Gyan.FFmpeg'; Label = 'FFmpeg (thuyết minh, video)' }
    )
    $installedAny = $false
    foreach ($tool in $optional) {
        if (Get-Command $tool.Command -ErrorAction SilentlyContinue) {
            Write-Ok "$($tool.Label): đã có"
            continue
        }
        if ((Test-Winget) -and (Confirm-Choice "Cài $($tool.Label) bằng winget?")) {
            winget install -e --id $tool.Id --accept-package-agreements --accept-source-agreements | Out-Host
            $installedAny = $true
        } else {
            Write-Host "Bỏ qua: $($tool.Label)"
        }
    }
    if ($installedAny) {
        $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
    }

    Write-Step 'Kiểm tra lại toàn bộ'
    return (Invoke-Doctor $py @())
}

function Get-FolderWarnings {
    $warnings = @()
    foreach ($variable in 'OneDrive', 'OneDriveCommercial', 'OneDriveConsumer') {
        $root = [Environment]::GetEnvironmentVariable($variable)
        if ($root -and $RepoRoot.StartsWith($root.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)) {
            $warnings += "Thư mục bộ công cụ nằm trong OneDrive ($root). Nên chuyển sang đường dẫn ngắn như D:\PPTmaster để tránh lỗi khoá file khi cài và khi xuất PPTX."
            break
        }
    }
    if ($RepoRoot.Length -gt $MaxRepoPathLength) {
        $warnings += "Đường dẫn thư mục bộ công cụ dài $($RepoRoot.Length) ký tự (nên dưới $MaxRepoPathLength). Nên chuyển sang đường dẫn ngắn như D:\PPTmaster."
    }
    if ($RepoRoot -like '*PPTmaster-main\PPTmaster-main*') {
        $warnings += 'Thư mục bị lồng PPTmaster-main\PPTmaster-main. Nên chuyển nội dung ra một thư mục ngắn như D:\PPTmaster.'
    }
    return $warnings
}

function Get-SetupPlan {
    $steps = @()
    $venvReady = Test-Path $VenvPython
    $basePython = $null
    if (-not $venvReady) {
        $basePython = Find-BasePython
        if (-not $basePython) {
            $method = if (Test-Winget) { 'winget' } else { 'python-org' }
            $steps += [pscustomobject]@{ step = 'python'; action = 'install'; method = $method }
        }
        $steps += [pscustomobject]@{ step = 'venv'; action = 'create'; method = 'python -m venv' }
    }
    $steps += [pscustomobject]@{ step = 'packages'; action = 'ensure'; method = 'pip' }
    if (-not (Test-Path (Join-Path $RepoRoot '.env'))) {
        $steps += [pscustomobject]@{ step = 'env'; action = 'create'; method = 'copy .env.example' }
    }
    $steps += [pscustomobject]@{ step = 'doctor'; action = 'run'; method = 'doctor.py --json' }
    return [pscustomobject]@{ BasePython = $basePython; VenvReady = $venvReady; Steps = $steps }
}

function Install-UserPython {
    if (Test-Winget) {
        Write-Log "Cài Python $PythonVersion cho tài khoản này bằng winget..."
        Invoke-Logged { winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements --disable-interactivity }
        $found = Find-BasePython
        if ($found) { return $found }
        Write-Log 'winget chưa cài được Python, chuyển sang bộ cài của python.org.'
    }
    $arch = if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') { 'arm64' } else { 'amd64' }
    $installer = $PythonInstallers[$arch]
    $file = Join-Path $env:TEMP "python-$PythonVersion-$arch.exe"
    Write-Log "Tải bộ cài Python $PythonVersion ($arch) từ python.org..."
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $installer.Url -OutFile $file -UseBasicParsing
    } catch {
        Set-SetupError 'python' "Không tải được bộ cài Python: $($_.Exception.Message)" 'Kiểm tra kết nối mạng. Máy trường có thể cần mở truy cập python.org (xem mục "Máy trường chặn cài đặt" trong docs/vi/xu-ly-loi.md).'
        return $null
    }
    $hash = (Get-FileHash -Path $file -Algorithm SHA256).Hash
    if ($hash -ne $installer.Sha256) {
        Remove-Item -Path $file -Force -ErrorAction SilentlyContinue
        Set-SetupError 'python' 'Bộ cài Python tải về không khớp mã SHA256 nên đã bị huỷ.' 'Thử lại sau; nếu vẫn lỗi, mạng có thể đang chặn hoặc sửa nội dung tải về (xem docs/vi/xu-ly-loi.md).'
        return $null
    }
    Write-Log 'Chạy bộ cài Python ở chế độ ngầm, chỉ cho tài khoản này...'
    try {
        $proc = Start-Process -FilePath $file -ArgumentList '/quiet', 'InstallAllUsers=0', 'PrependPath=1', 'Include_launcher=1', 'InstallLauncherAllUsers=0', 'Include_test=0' -Wait -PassThru -WindowStyle Hidden
    } catch {
        Set-SetupError 'python' "Không chạy được bộ cài Python: $($_.Exception.Message)" 'Máy có thể đang chặn chạy bộ cài; xem mục "Máy trường chặn cài đặt" trong docs/vi/xu-ly-loi.md.'
        return $null
    } finally {
        Remove-Item -Path $file -Force -ErrorAction SilentlyContinue
    }
    $found = Find-BasePython
    if (-not $found) {
        Set-SetupError 'python' "Bộ cài Python kết thúc (mã $($proc.ExitCode)) nhưng không tìm thấy Python." 'Cài Python 3.12 thủ công theo docs/vi/cai-dat-windows.md, hoặc nhờ bộ phận IT (xem mục "Máy trường chặn cài đặt" trong docs/vi/xu-ly-loi.md).'
        return $null
    }
    return $found
}

function Get-DoctorReport([string[]]$DoctorArgs) {
    $raw = & $VenvPython $Doctor --json @DoctorArgs
    $text = ($raw | Out-String).Trim()
    if (-not $text) { return $null }
    try { return ($text | ConvertFrom-Json) } catch { return $null }
}

# venv hỏng (python.exe rỗng, Python gốc đã gỡ) có thể ném lỗi thay vì trả mã thoát, nên bọc try/catch.
function Test-VenvPython([string[]]$Arguments) {
    $global:LASTEXITCODE = 1
    try { Invoke-Logged { & $VenvPython @Arguments } } catch { Write-Log "$_"; return $false }
    return ($LASTEXITCODE -eq 0)
}

function Test-PackagesOk($Report) {
    if (-not $Report) { return $false }
    $upstreamOk = $false
    foreach ($check in $Report.checks) {
        if ($check.name -eq 'Thư viện Python') { $upstreamOk = [bool]$check.ok }
        # Doctor cũ không có mục này thì coi như ổn; có mục mà báo thiếu thì phải cài.
        if ($check.name -eq 'Thư viện lớp Việt' -and -not [bool]$check.ok) { return $false }
    }
    return $upstreamOk
}

function Write-SetupResult([bool]$Ready, $Installed, $Warnings, $Checks) {
    $python = if (Test-Path $VenvPython) { $VenvPython } else { $null }
    Write-Json ([pscustomobject]@{
        ready     = $Ready
        python    = $python
        installed = @($Installed)
        warnings  = @($Warnings)
        checks    = @($Checks)
        error     = $script:SetupError
    })
}

function Invoke-AutoSetup {
    $warnings = @(Get-FolderWarnings)
    if ($PlanOnly) {
        $plan = Get-SetupPlan
        $found = if ($plan.VenvReady) { $VenvPython } else { $plan.BasePython }
        Write-Json ([pscustomobject]@{ python_found = $found; steps = @($plan.Steps); warnings = $warnings })
        return 0
    }
    foreach ($warning in $warnings) { Write-Log "[CẢNH BÁO] $warning" }
    $installed = @()

    if (-not (Test-Path $VenvPython)) {
        $base = Find-BasePython
        if (-not $base) {
            $base = Install-UserPython
            if (-not $base) { Write-SetupResult $false $installed $warnings @(); return 1 }
            $installed += 'python'
        }
        Write-Log "Tạo môi trường Python riêng (venv) bằng $base..."
        Invoke-Logged { & $base -m venv $VenvDir }
        if (-not (Test-Path $VenvPython)) {
            Set-SetupError 'venv' 'Không tạo được thư mục venv.' 'Xoá thư mục venv trong bộ công cụ (nếu có) rồi chạy lại lệnh cài.'
            Write-SetupResult $false $installed $warnings @()
            return 1
        }
        $installed += 'venv'
    }

    $brokenVenvMessage = 'Môi trường venv bị hỏng hoặc tạo dở.'
    $brokenVenvFix = 'Xoá thư mục venv trong bộ công cụ rồi chạy lại lệnh cài.'
    if (-not (Test-VenvPython @('-c', 'import sys'))) {
        Set-SetupError 'venv' $brokenVenvMessage $brokenVenvFix
        Write-SetupResult $false $installed $warnings @()
        return 1
    }

    if (-not (Test-PackagesOk (Get-DoctorReport @('--no-smoke')))) {
        if (-not (Test-VenvPython @('-m', 'pip', '--version'))) {
            Set-SetupError 'venv' $brokenVenvMessage $brokenVenvFix
            Write-SetupResult $false $installed $warnings @()
            return 1
        }
        $pipCode = 1
        for ($attempt = 1; $attempt -le 2 -and $pipCode -ne 0; $attempt++) {
            Write-Log "Cài thư viện Python (lần $attempt, có thể mất vài phút)..."
            Invoke-Logged { & $VenvPython -m pip install --upgrade pip }
            Invoke-Logged { & $VenvPython -m pip install -r (Join-Path $RepoRoot 'requirements.txt') }
            $pipCode = $LASTEXITCODE
        }
        if ($pipCode -ne 0) {
            $packagesFix = 'Xem mục "Máy trường chặn cài đặt" trong docs/vi/xu-ly-loi.md; mạng trường có thể cần mở truy cập pypi.org và files.pythonhosted.org.'
            if ($warnings.Count -gt 0) {
                $packagesFix += ' Nếu thư mục có cảnh báo đường dẫn dài hoặc OneDrive, xem thêm mục "Đường dẫn quá dài" trong docs/vi/xu-ly-loi.md.'
            }
            Set-SetupError 'packages' 'Cài thư viện Python thất bại.' $packagesFix
            Write-SetupResult $false $installed $warnings @()
            return 1
        }
        Invoke-Logged { & $VenvPython -m pip install -r (Join-Path $RepoRoot 'tools\vi\requirements-vi.txt') }
        if ($LASTEXITCODE -ne 0) {
            $warnings += 'Chưa cài được python-docx (thư viện soạn đề). Tạo slide vẫn dùng bình thường; khi cần soạn đề, chạy: python -m pip install -r tools/vi/requirements-vi.txt'
        }
        $installed += 'packages'
    }

    $envFile = Join-Path $RepoRoot '.env'
    if (-not (Test-Path $envFile)) {
        Copy-Item (Join-Path $RepoRoot '.env.example') $envFile
        $installed += 'env'
    }

    Write-Log 'Kiểm tra lại toàn bộ (có xuất thử một file PPTX)...'
    $report = Get-DoctorReport @()
    if (-not $report) {
        Set-SetupError 'doctor' 'Không đọc được kết quả kiểm tra môi trường.' 'Chạy KIEM-TRA.bat để xem chi tiết.'
        Write-SetupResult $false $installed $warnings @()
        return 1
    }
    $ready = [bool]$report.ready
    Write-SetupResult $ready $installed $warnings @($report.checks)
    if ($ready) { return 0 }
    return 1
}

function Find-ToolDir([string]$ToolName) {
    if ($ToolName -eq 'chromium') {
        if (-not $env:LOCALAPPDATA) { return $null }
        $browsers = Join-Path $env:LOCALAPPDATA 'ms-playwright'
        if (-not (Test-Path $browsers)) { return $null }
        $folder = @(Get-ChildItem -Path $browsers -Directory -Filter 'chromium-*' -ErrorAction SilentlyContinue | Sort-Object Name)
        if ($folder.Count -eq 0) { return $null }
        # R9: the browser folder alone is not enough — tools/vi/video.py runs
        # under $VenvPython and needs the playwright pip package importable
        # there too, or slide capture fails even though this returns a path.
        if (-not (Test-Path $VenvPython)) { return $null }
        if (-not (Test-VenvPython @('-c', 'import playwright'))) { return $null }
        return $folder[-1].FullName
    }
    $exe = $OptionalTools[$ToolName].Exe
    $cmd = Get-Command $exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cmd) { return (Split-Path -Path $cmd.Source -Parent) }
    if (-not $env:LOCALAPPDATA) { return $null }
    $candidates = @()
    if ($ToolName -eq 'ffmpeg') {
        $candidates += Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links\ffmpeg.exe'
        $packages = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages'
        if (Test-Path $packages) {
            foreach ($folder in @(Get-ChildItem -Path $packages -Directory -Filter 'Gyan.FFmpeg*' -ErrorAction SilentlyContinue)) {
                $candidates += @(Get-ChildItem -Path $folder.FullName -Filter 'ffmpeg.exe' -Recurse -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
            }
        }
    } else {
        $candidates += Join-Path $env:LOCALAPPDATA 'Pandoc\pandoc.exe'
    }
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) { return (Split-Path -Path $candidate -Parent) }
    }
    return $null
}

function Invoke-Tool {
    if (-not $Name -or -not $OptionalTools.ContainsKey($Name)) {
        $message = if ($Name) { "Tên công cụ không hợp lệ: $Name." } else { 'Thiếu tham số -Name.' }
        $toolValue = if ($Name) { $Name } else { $null }
        Write-Json ([pscustomobject]@{ tool = $toolValue; found = $false; installed = $false; dir = $null; error = [pscustomobject]@{ step = 'tool'; message = $message; fix = 'Chạy lại với -Name ffmpeg, -Name pandoc hoặc -Name chromium.' } })
        return 1
    }
    $tool = $OptionalTools[$Name]
    $dir = Find-ToolDir $Name
    if ($PlanOnly) {
        $steps = @()
        if (-not $dir) {
            $method = if ($Name -eq 'chromium') { 'pip+playwright' } elseif (Test-Winget) { 'winget' } else { 'manual' }
            $steps += [pscustomobject]@{ step = $Name; action = 'install'; method = $method }
        }
        Write-Json ([pscustomobject]@{ tool = $Name; found = [bool]$dir; dir = $dir; steps = @($steps) })
        return 0
    }
    if ($dir) {
        Write-Json ([pscustomobject]@{ tool = $Name; found = $true; installed = $false; dir = $dir; error = $null })
        return 0
    }
    if ($Name -eq 'chromium') {
        if (-not (Test-Path $VenvPython)) {
            Write-Json ([pscustomobject]@{ tool = $Name; found = $false; installed = $false; dir = $null; error = [pscustomobject]@{ step = 'tool'; message = 'Chưa có môi trường Python riêng (venv) để cài Chromium.'; fix = 'Chạy lệnh cài đặt trước: -Action setup -Auto' } })
            return 1
        }
        Write-Log 'Cài Playwright và tải Chromium (khoảng 150-300 MB, có thể mất vài phút)...'
        Invoke-Logged { & $VenvPython -m pip install playwright }
        Invoke-Logged { & $VenvPython -m playwright install chromium }
        $dir = Find-ToolDir $Name
        if (-not $dir) {
            Write-Json ([pscustomobject]@{ tool = $Name; found = $false; installed = $false; dir = $null; error = [pscustomobject]@{ step = 'tool'; message = 'Không tải được Chromium.'; fix = "Kiểm tra mạng rồi chạy lại; hướng dẫn thủ công: $($tool.Manual)" } })
            return 1
        }
        Write-Json ([pscustomobject]@{ tool = $Name; found = $true; installed = $true; dir = $dir; error = $null })
        return 0
    }
    if (-not (Test-Winget)) {
        Write-Json ([pscustomobject]@{ tool = $Name; found = $false; installed = $false; dir = $null; error = [pscustomobject]@{ step = 'tool'; message = "Máy không có winget nên không tự cài được $Name."; fix = "Tải và cài thủ công tại $($tool.Manual)" } })
        return 1
    }
    $id = $tool.Id
    Write-Log "Cài $Name cho tài khoản này bằng winget..."
    Invoke-Logged { winget install -e --id $id --scope user --silent --accept-package-agreements --accept-source-agreements --disable-interactivity }
    $dir = Find-ToolDir $Name
    if (-not $dir) {
        Write-Json ([pscustomobject]@{ tool = $Name; found = $false; installed = $false; dir = $null; error = [pscustomobject]@{ step = 'tool'; message = "winget không cài được $Name."; fix = "Tải và cài thủ công tại $($tool.Manual)" } })
        return 1
    }
    Write-Json ([pscustomobject]@{ tool = $Name; found = $true; installed = $true; dir = $dir; error = $null })
    return 0
}

function Invoke-Check {
    $py = Resolve-RunPython
    if (-not $py) { Write-Host 'Hãy bấm CAI-DAT.bat trước.'; return 1 }
    return (Invoke-Doctor $py @())
}

function Invoke-Update {
    if (-not (Test-Path (Join-Path $RepoRoot '.git'))) {
        Write-Fail 'Thư mục này được tải dạng ZIP nên không tự cập nhật được.'
        Write-Host 'Tải bản mới tại https://github.com/luonghaianh1208/2anh-studio rồi chép thư mục projects\ và file .env của bạn sang.'
        return 1
    }
    $py = Resolve-RunPython
    if (-not $py) { Write-Host 'Hãy bấm CAI-DAT.bat trước.'; return 1 }
    Write-Step 'Tải bản mới nhất'
    & $py.Path (Join-Path $RepoRoot 'skills\ppt-master\scripts\update_repo.py') | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Fail 'Cập nhật thất bại.'
        Write-Host "Nếu thông báo có 'Tracked local changes' là bạn đã sửa file của bộ công cụ. Cách xử lý: $FixDoc (mục Cập nhật thất bại)"
        return 1
    }
    Write-Step 'Kiểm tra nhanh sau cập nhật'
    return (Invoke-Doctor $py @('--no-smoke'))
}

Push-Location $RepoRoot
try {
    switch ($Action) {
        'setup' { if ($Auto -or $PlanOnly) { $code = Invoke-AutoSetup } else { $code = Invoke-Setup } }
        'check' { $code = Invoke-Check }
        'update' { $code = Invoke-Update }
        'tool' { $code = Invoke-Tool }
    }
} finally {
    Pop-Location
}
exit ([int]($code | Select-Object -Last 1))
