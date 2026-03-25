@echo off
echo === Olympic Project - Data Download ===
echo.

cd /d "%~dp0.."

echo [1/3] World Bank (GDP, Population, GNI)...
python scripts/download_world_bank.py
echo.

echo [2/3] Eurostat (Government expenditure COFOG)...
python scripts/download_eurostat.py
echo.

echo [3/3] UNDP HDI...
python scripts/download_undp_hdi.py
echo.

echo === Automatic downloads done ===
echo.
echo Next: Run Kaggle downloads (requires kaggle token):
echo   python scripts/download_kaggle.py
echo.
echo Then: See scripts/README_manual_downloads.md for WVS + ESS steps.
pause
