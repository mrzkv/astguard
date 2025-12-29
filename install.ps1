# 0. Проверка прав администратора и перезапуск при необходимости
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Запрос прав администратора для установки..." -ForegroundColor Yellow
    $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    try {
        Start-Process powershell.exe -ArgumentList $arguments -Verb RunAs -Wait
        exit
    } catch {
        Write-Host "Ошибка: Не удалось получить права администратора. Пожалуйста, запустите PowerShell от имени администратора вручную." -ForegroundColor Red
        exit 1
    }
}

# PowerShell script to install ib-static-analyzer (astguard)

$ErrorActionPreference = "Stop"

Write-Host "=== Установка ib-static-analyzer (astguard) ===" -ForegroundColor Cyan

# 1. Проверка наличия Python
try {
    $pythonVersionStr = python --version 2>$null
    if ($null -eq $pythonVersionStr) {
        $pythonVersionStr = python3 --version 2>$null
    }
} catch {
    $pythonVersionStr = $null
}

if ($null -eq $pythonVersionStr) {
    Write-Host "Ошибка: Python не найден. Пожалуйста, установите Python 3.8 или выше с сайта python.org" -ForegroundColor Red
    exit 1
}

# 2. Проверка версии Python
# Извлекаем версию из строки типа "Python 3.10.12"
if ($pythonVersionStr -match "Python (\d+\.\d+)") {
    $version = [version]$matches[1]
    if ($version -lt [version]"3.8") {
        Write-Host "Ошибка: Требуется Python версии 3.8 или выше. У вас установлена версия $($matches[1])." -ForegroundColor Red
        exit 1
    }
}

# 3. Проверка наличия Git
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Ошибка: git не найден. Пожалуйста, установите git (https://git-scm.com/)." -ForegroundColor Red
    exit 1
}

# 4. Установка пакета из GitHub
$REPO_URL = "git+https://github.com/mrzkv/ib-static-analyzer.git"

Write-Host "Установка пакета из GitHub..." -ForegroundColor Cyan

try {
    # 4.1 Пытаемся найти путь к Scripts Python
    try {
        $pythonScripts = (python -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>$null).Trim()
        if ($null -ne $pythonScripts -and (Test-Path $pythonScripts)) {
            if ($env:PATH -notlike "*$pythonScripts*") {
                Write-Host "Добавление $pythonScripts в PATH текущей сессии..." -ForegroundColor Gray
                $env:PATH = "$pythonScripts;" + $env:PATH
                
                # Также пытаемся добавить в пользовательский PATH на постоянной основе, если его там нет
                $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
                if ($userPath -notlike "*$pythonScripts*") {
                    Write-Host "Добавление $pythonScripts в пользовательский PATH навсегда..." -ForegroundColor Gray
                    # Аккуратно объединяем, чтобы не было лишних точек с запятой
                    if ($userPath -and !$userPath.EndsWith(";")) { $userPath += ";" }
                    [Environment]::SetEnvironmentVariable("Path", "$userPath$pythonScripts", "User")
                }
            }
        }
    } catch {
        Write-Host "Предупреждение: Не удалось автоматически определить путь к Python Scripts." -ForegroundColor Yellow
    }

    python -m pip install $REPO_URL
    Write-Host "`nУстановка завершена успешно!" -ForegroundColor Green
    
    # 4.2 Проверка доступности команды в текущей сессии
    if (!(Get-Command astguard -ErrorAction SilentlyContinue)) {
        Write-Host "`nВнимание: Команда 'astguard' может быть недоступна в этом окне без перезапуска." -ForegroundColor Yellow
        Write-Host "Попробуйте закрыть и снова открыть PowerShell или выполнить:" -ForegroundColor Yellow
        Write-Host "  `$env:PATH = `"$pythonScripts;`" + `$env:PATH" -ForegroundColor Cyan
    }

    Write-Host "`nТеперь вы можете использовать команду: " -NoNewline
    Write-Host "astguard --help" -ForegroundColor Cyan
} catch {
    Write-Host "Ошибка при установке через pip. Попробуйте запустить PowerShell от имени администратора." -ForegroundColor Red
    exit 1
}
