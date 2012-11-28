VERSION := $(shell python -c 'import settings; print(settings.VERSAO)')

BUILD_DIR := _build
BUILD_NAME := vestat_v$(VERSION)

DJANGO_APP_DIRS := $(shell python -c 'import settings; print("\n".join(app[7:] for app in settings.INSTALLED_APPS if app.startswith("vestat")))')
DJANGO_FILES := manage.py settings.py middleware.py urls.py views.py media templates
PYTHON_PACKAGE_FILES := __init__.py requirements.txt
INSTALL_FILES = deps trecos instalar.bat instalar.py

BUILD_FILES := $(DJANGO_FILES) $(DJANGO_APP_DIRS) $(PYTHON_PACKAGE_FILES) $(INSTALL_FILES)

$(BUILD_DIR):
	mkdir $(BUILD_DIR)

build: $(BUILD_DIR) $(BUILD_FILES)
	tar czf $(BUILD_DIR)/$(BUILD_NAME).tar.gz $(BUILD_FILES) \
		--exclude-vcs \
		--exclude='venv' \
		--exclude='*.pyc' \
		--exclude='__pycache__' \
		--transform "s@^@$(BUILD_NAME)/vestat/@"

test:
	python2 manage.py test caixa contabil

clean:
	rm _build -rf
