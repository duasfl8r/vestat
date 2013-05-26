VERSION := $(shell cd vestat && python -c 'import settings; print(settings.VERSAO)')

BUILD_DIR := _build
BUILD_NAME := vestat_v$(VERSION)
DOCS_NAME = documentacao_v$(VERSION)

BUILD_FILES := CHANGELOG.txt deps requirements.txt vestat instalar.bat instalar.py

$(BUILD_DIR):
	mkdir $(BUILD_DIR)

.PHONY: docs
docs:
	cd docs && make html
	rm $(BUILD_DIR)/$(DOCS_NAME) --recursive --force
	mv docs/_build/html $(BUILD_DIR)/$(DOCS_NAME) --force

build: $(BUILD_DIR) $(BUILD_FILES) docs
	rm $(DOCS_NAME) --force --recursive
	mv $(BUILD_DIR)/$(DOCS_NAME) .

	tar czf $(BUILD_DIR)/$(BUILD_NAME).tar.gz $(BUILD_FILES) $(DOCS_NAME) \
		--exclude-vcs \
		--exclude='venv' \
		--exclude='*.pyc' \
		--exclude='__pycache__' \
		--exclude='vestat.sqlite' \
		--transform "s@^@$(BUILD_NAME)/@"

	mv $(DOCS_NAME) $(BUILD_DIR)

test:
	cd vestat && python manage.py test caixa contabil relatorios feriados

clean:
	cd $(BUILD_DIR) && rm $(BUILD_NAME).tar.gz $(DOCS_NAME) \
		--recursive \
		--force
