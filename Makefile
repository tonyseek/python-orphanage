.PHONY: help deps test docs dist dist-wheel dist-repair clean

help:
	@printf "Commands:\n"
	@printf "  help\tShows this help information.\n"
	@printf "  deps\tCompiles and locks dependencies.\n"
	@printf "  test\tRuns test via tox.\n"
	@printf "  docs\tGenerates documents via tox and sphinx.\n"
	@printf "  dist\tBuilds distribution packages.\n"
	@printf "  clean\tRemoves all untracked files.\n"

deps:
	pip-compile --output-file docs/requirements.txt docs/requirements.in
	pip-compile --output-file requirements-test.txt requirements-test.in

test:
	tox -re "$(shell tox -l | grep -v docs | paste -s -d ',' -)" --skip-missing-interpreters
	@printf "\nopen tests/htmlcov/index.html tests/htmlcov/c-ext/index.html\n"

docs:
	tox -e docs
	@printf "\nopen docs/_build/html/index.html\n"

dist:
	rm -rf dist
	python setup.py egg_info $(options) sdist
	# Build for macOS
	make dist-wheel PYTHON=python2.7 options="$(options)"
	make dist-wheel PYTHON=python3.6 options="$(options)"
	make dist-wheel PYTHON=pypy options="$(options)"
	make dist-wheel PYTHON=pypy3 options="$(options)"
	# Build for Linux
	docker run --rm -v $(PWD):/srv python:2.7 make -C /srv dist-wheel PYTHON=python2.7 options="$(options)"
	docker run --rm -v $(PWD):/srv python:3.6 make -C /srv dist-wheel PYTHON=python3.6 options="$(options)"
	docker run --rm -v $(PWD):/srv pypy:2 make -C /srv dist-wheel PYTHON=pypy options="$(options)"
	docker run --rm -v $(PWD):/srv pypy:3 make -C /srv dist-wheel PYTHON=pypy3 options="$(options)"
	# Repair for Linux
	docker run --rm -v $(PWD):/srv quay.io/pypa/manylinux1_x86_64 make -C /srv dist-repair

dist-wheel:
	$(PYTHON) setup.py egg_info $(options) bdist_wheel

dist-repair:
	find dist -name '*-linux_x86_64.whl' -exec auditwheel repair -w dist {} \;
	find dist -name '*-linux_x86_64.whl' -delete

clean:
	git clean -fXd --exclude=.tox
