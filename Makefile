help:
	@echo '                                                                                             '
	@echo 'Makefile for the External Grader                                                             '
	@echo '                                                                                             '
	@echo 'Usage:                                                                                       '
	@echo '    make requirements          install requirements                                          '
	@echo '    make requirements-test     install test requirements                                     '
	@echo '    make test                  run tests                                                     '
	@echo '    make compose               build and launch prod containers via docker-compose           '
	@echo '    make compose-test          build and launch test containers via docker-compose           '
	@echo '    make update                reset changes in directory and pull the newest commit from git'
	@echo '                                                                                             '

requirements:
	pip install -qr requirements/requirements.txt

requirements-test: requirements
	pip install -qr requirements/requirements-test.txt

test: requirements-test
	pytest -v

compose:
	docker-compose build
	docker-compose up -d

compose-test:
	docker-compose -f docker-compose.test.yml build
	docker-compose -f docker-compose.test.yml up --exit-code-from grader
	docker-compose -f docker-compose.test.yml down

update:
	git reset --hard
	git pull https://github.com/Ragnaruk/external_grader.git

.PHONY: requirements requirements-test test compose compose-test update