VERSION := $(shell python -c 'import settings; print(settings.VERSAO)')

BUILD_DIR := _build
BUILD_NAME := vestat_v$(VERSION)
BUILD_FILES := caixa config deps instalar.bat instalar.py manage.py media \
			  middleware.py relatorios requirements.txt settings.py templates \
			  trecos urls.py views.py

$(BUILD_DIR):
	mkdir $(BUILD_DIR)

build: $(BUILD_DIR) $(BUILD_FILES)
	tar czf $(BUILD_DIR)/$(BUILD_NAME).tar.gz $(BUILD_FILES) \
		--exclude-vcs \
		--exclude='venv' \
		--exclude='*.pyc' \
		--exclude='__pycache__' \
		--transform "s@^@$(BUILD_NAME)/@"

test:
	python2 manage.py test caixa

clean:
	rm _build -rf
