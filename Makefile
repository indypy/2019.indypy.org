.PHONY: virtualenv
virtualenv:
	rm -rf env
	python3 -m venv env
	env/bin/pip install -r requirements.txt

.PHONY: build
build: virtualenv
	env/bin/lektor clean --yes
	env/bin/lektor build

.PHONY: serve
serve: virtualenv
	env/bin/lektor serve
