.PHONY: help deps test docs

help:
	@printf "Commands:\n"
	@printf "  help\tShows this help information.\n"
	@printf "  deps\tCompiles and locks dependencies.\n"
	@printf "  test\tRuns test via tox.\n"
	@printf "  docs\tGenerates documents via tox and sphinx.\n"

deps:
	pip-compile --output-file docs/requirements.txt docs/requirements.in
	pip-compile --output-file requirements-test.txt requirements-test.in

test:
	tox -re "$(shell tox -l | grep -v docs | paste -s -d ',' -)" --skip-missing-interpreters
	@printf "\nopen tests/htmlcov/index.html\n"
	@printf "\nopen tests/htmlcov/gcov.html\n"

docs:
	tox -e docs
	@printf "\nopen docs/_build/html/index.html\n"
