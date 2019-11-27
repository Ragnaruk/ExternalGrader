help:
	@echo '                                                                                             '
	@echo 'Makefile for the External Grader                                                             '
	@echo '                                                                                             '
	@echo 'Usage:                                                                                       '
	@echo '    make requirements              install requirements                                      '
	@echo '    make requirements-test         install test requirements                                 '
	@echo '    make requirements-dev          install dev requirements                                  '
	@echo '    make test                      run tests                                                 '
	@echo '    make test-cov                  run tests with coverage                                   '
	@echo '    make format                    reformat all python files                                 '
	@echo '    make prepare                   build images required for grading                         '
	@echo '    make compose                   build and launch prod containers via docker-compose       '
	@echo '    make update                    reset changes and pull the newest version from git        '
	@echo '                                                                                             '

requirements:
	pip install -qr requirements/requirements.txt

requirements-test: requirements
	pip install -qr requirements/requirements-test.txt

requirements-dev: requirements-test
	pip install -qr requirements/requirements-dev.txt

test:
	pytest -vvv

test-cov:
	pytest --cov-report term-missing --cov=./ -vvv

black:
	black .

compose:
	docker-compose build
	docker-compose up -d

compose-reqs:
	docker-compose -f docker-compose.reqs.yml build

update:
	git reset --hard
	git pull https://github.com/Ragnaruk/external_grader.git

.PHONY: requirements requirements-test requirements-dev test test-cov prepare compose update