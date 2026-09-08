$env:KMP_DUPLICATE_LIB_OK = "TRUE"
Write-Host "Launching CTDI Air Pollution Imputation Dashboard..." -ForegroundColor Cyan
py -3.13 -m streamlit run app.py
