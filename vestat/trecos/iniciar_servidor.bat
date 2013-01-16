cls
@echo off
path = C:\vestat\Python27;C:\vestat\\Python27\Scripts;C:\vestat\\Python27\Lib\site-packages\django\bin;C:\vestat\\Utilities;C:\vestat\\Utilities\Exemaker;C:\vestat\\Utilities\Npp;C:\vestat\\Utilities\Sqlite;C:\vestat\\Utilities\Mercurial;C:\vestat\\Utilities\Winmerge;%PATH%
set PYTHONPATH=C:\vestat\Python27;C:\vestat\Python27\Lib\site-packages
exemaker -i "C:\vestat\\Python27\python.exe" "C:\vestat\\Python27\Lib\site-packages\django\bin\django-admin.py" "C:\vestat\\Python27\Lib\site-packages\django\bin" 1>nul 2>&1
cd vestat
python manage.py runserver
