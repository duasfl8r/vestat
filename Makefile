VERSION := $(shell cd vestat && python -c 'import settings; print(settings.VERSAO)')

BUILD_DIR := _build
BUILD_NAME := vestat_v$(VERSION)

BUILD_FILES := CHANGELOG.txt deps requirements.txt vestat

$(BUILD_DIR):
	mkdir $(BUILD_DIR)

build: $(BUILD_DIR) $(BUILD_FILES)
	tar czf $(BUILD_DIR)/$(BUILD_NAME).tar.gz $(BUILD_FILES) \
		--exclude-vcs \
		--exclude='venv' \
		--exclude='*.pyc' \
		--exclude='__pycache__' \
		--exclude='vestat.sqlite' \
		--transform "s@^@$(BUILD_NAME)/vestat/@"

test:
	cd vestat && python manage.py test caixa contabil relatorios feriados

clean:
	rm _build -rf
