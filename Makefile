
BUILD_DIR := _build

VERSION := $(shell cd vestat; python -c 'import settings; print(settings.VERSAO)')
BUILD_NAME := vestat_v$(VERSION)

BUILD_FILES := deps docs trecos CHANGELOG.txt vestat

$(BUILD_DIR):
	mkdir $(BUILD_DIR)

build: $(BUILD_DIR)
	tar czf $(BUILD_DIR)/$(BUILD_NAME).tar.gz $(BUILD_FILES) \
		--exclude-vcs \
		--exclude='venv' \
		--exclude='*.pyc' \
		--exclude='__pycache__' \
		--transform "s@^@$(BUILD_NAME)/@"

test:
	python2 manage.py test caixa contabil

clean:
	rm _build -rf
