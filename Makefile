.PHONY: build
build:
	@# Build the docker image for hello-world
	docker build --pull -t hello-world .

.PHONY: test
test:
	@# Run unit tests for hello-world
	docker run hello-world python3 manage.py test


.PHONY: publish
publish: test
	@# Upload hello-world to our PyPi server
	@docker run hello-world python3 manage.py upload --username $(DEVPI_USERNAME) --password $(DEVPI_PASSWORD) --index https://pypi.lundalogik.com:3443/lime/develop/+simple/


.PHONY: pytest
pytest:
	docker-compose run app py.test -s


.PHONY: ptw
ptw:
	@# Start watching file system for changes and re-run tests when a change is detected.
	docker-compose run app ptw -- --no-print-logs
