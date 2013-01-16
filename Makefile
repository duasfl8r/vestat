VERSION := $(shell cd vestat && python -c 'import settings; print(settings.VERSAO)')

BUILD_DIR := _build

BUILD_FILES := CHANGELOG.txt deps requirements.txt vestat

$(BUILD_DIR):
	mkdir $(BUILD_DIR)

build: $(BUILD_DIR)
	tar czf $(BUILD_DIR)/$(BUILD_NAME).tar.gz $(BUILD_FILES) \
		--exclude-vcs \
		--exclude='venv' \
		--exclude='*.pyc' \
		--exclude='__pycache__' \
		--exclude='vestat.sqlite' \
		--transform "s@^@$(BUILD_NAME)/vestat/@"

test:
	cd vestat && python2 manage.py test caixa contabil relatorios

clean:
	rm _build -rf
