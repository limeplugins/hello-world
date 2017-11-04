.PHONY: help
help:
	@# Print this help text
	@./make-help.py $(MAKEFILE_LIST)


.PHONY: test
test:
	@# Run unit tests for hello-world

	docker build --pull -t hello-world .
	docker run hello-world py.test


.PHONY: ptw
ptw:
	@# Start watching file system for changes and re-run tests when a change is detected.

	docker-compose run app ptw


.PHONY: flake
flake:
	@# Run flake to check for style errors

	docker-compose run app flake8
