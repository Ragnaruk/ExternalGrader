help:
	@echo '                                                                                             '
	@echo 'Makefile for the External Grader                                                             '
	@echo '                                                                                             '
	@echo 'Usage:                                                                                       '
	@echo '    make requirements          install requirements                                          '
	@echo '    make requirements-test     install test requirements                                     '
	@echo '    make test                  run tests                                                     '
	@echo '    make update                reset changes in directory and pull the newest commit from git'
	@echo '    make compose               rebuild and launch containers via docker-compose              '
	@echo '                                                                                             '

requirements:
	pip install -qr requirements/requirements.txt

requirements-test: requirements
	pip install -qr requirements/requirements-test.txt

test: requirements-test
	pytest -v

update:
	git reset --hard
	git pull https://github.com/Ragnaruk/external_grader.git

compose:
	docker-compose build
	docker-compose up -d
