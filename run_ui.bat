@echo off
set KMP_DUPLICATE_LIB_OK=TRUE
echo Launching CTDI Air Pollution Imputation Dashboard...
py -3.13 -m streamlit run app.py
pause
