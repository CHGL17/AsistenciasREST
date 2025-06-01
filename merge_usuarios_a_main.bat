@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo 🔁 SUBIDA AUTOMÁTICA: RAMA USUARIOS → MAIN
echo ===============================================

REM Paso 1: Asegúrate de estar en la rama usuarios
git checkout usuarios
IF ERRORLEVEL 1 (
    echo ❌ No se pudo cambiar a la rama 'usuarios'.
    pause
    exit /b
)

echo.
echo 📦 Agregando cambios actuales...
git add .
set /p MSG="📝 Escribe el mensaje del commit: "
git commit -m "%MSG%"

REM Paso 2: Actualizar y hacer rebase con main
echo.
echo 🔄 Haciendo rebase de usuarios con origin/main...
git fetch origin
git rebase origin/main

IF ERRORLEVEL 1 (
    echo ⚠️  Hubo conflictos en el rebase.
    echo 🔧 Resuélvelos, haz 'git add' y luego 'git rebase --continue'.
    pause
    exit /b
)

REM Paso 3: Subir rama usuarios
echo.
echo ⬆️ Subiendo rama usuarios a origin (force push por rebase)...
git push origin usuarios --force

REM Paso 4: Cambiar a main y hacer merge
echo.
echo 🔁 Cambiando a main...
git checkout main

echo.
echo ⬇️ Actualizando main con origin...
git pull origin main

echo.
echo 🔀 Haciendo merge desde usuarios a main...
git merge usuarios

REM Paso 5: Subir cambios finales a origin/main
echo.
echo ⬆️ Subiendo main a origin...
git push origin main

echo.
echo ✅ ¡Listo! Rama 'usuarios' fusionada exitosamente a 'main'.
pause
