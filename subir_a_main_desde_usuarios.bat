@echo off
setlocal enabledelayedexpansion

echo ============================================
echo 🔁 Subida limpia de cambios: USUARIOS → MAIN
echo ============================================

REM Verifica que estés en la rama correcta
git branch --show-current
echo.
set /p CONFIRM="¿Estás en la rama 'usuarios'? (s/n): "
if /I "%CONFIRM%" NEQ "s" (
    echo ❌ Por favor cambia a la rama 'usuarios' antes de ejecutar este script.
    exit /b
)

echo.
echo 📦 Guardando cambios actuales...
git add .
set /p MSG="Escribe el mensaje del commit: "
git commit -m "%MSG%"

echo.
echo 🔄 Rebase con la rama 'main' (origin/master)...
git fetch origin
git rebase origin/master

IF ERRORLEVEL 1 (
    echo ⚠️  Hubo conflictos en el rebase.
    echo ✔️  Resuélvelos manualmente, haz 'git add' y luego 'git rebase --continue'.
    pause
    exit /b
)

echo.
echo ⬆️ Subiendo a origin/usuarios con --force...
git push origin usuarios --force

echo.
echo ✅ ¡Listo! Ya puedes crear un Pull Request desde 'usuarios' hacia 'main' en GitHub.
pause
