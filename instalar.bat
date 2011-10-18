cls
@echo off
path = trecos\Python27;trecos\\Python27\Scripts;trecos\\Python27\Lib\site-packages\django\bin;trecos\\Utilities;trecos\\Utilities\Exemaker;trecos\\Utilities\Npp;trecos\\Utilities\Sqlite;trecos\\Utilities\Mercurial;trecos\\Utilities\Winmerge;%PATH%
set PYTHONPATH=trecos\%\Python27;trecos\%\Python27\Lib\site-packages
exemaker -i "trecos\\Python27\python.exe" "trecos\\Python27\Lib\site-packages\django\bin\django-admin.py" "trecos\\Python27\Lib\site-packages\django\bin" 1>nul 2>&1
python instalar.py
