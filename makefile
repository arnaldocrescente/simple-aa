default: start

project:=simple-aa
service:=core
COMMIT_HASH = $(shell git rev-parse --verify HEAD)

UID = $(shell id -u)
GID = $(shell id -g)

HELP_WIDTH := $(shell grep -h '^[a-z][^ ]*:.*\#\#' $(MAKEFILE_LIST) 2>/dev/null | \
	cut -d':' -f1 | awk '{printf "%d\n", length}' | sort -rn | head -1)

help:  ## Show this help
	@echo "\nSpecify a command. The choices are:\n"
	@grep -Eh '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[0;36m%-$(HELP_WIDTH)s  \033[m %s\n", $$1, $$2}'
	@echo ""

.PHONY: start
start:  ## Start the project
	docker compose -p ${project} up -d

.PHONY: stop
stop:  ## Stop the project
	docker compose -p ${project} stop

.PHONY: down
down:  ## Stop and remove the project containers
	docker compose -p ${project} down

.PHONY: restart
restart: stop start  ## Stop and start the project

.PHONY: logs
logs:  ## Show project's logs service=SERVICE_NAME, default core
	docker compose -p ${project} logs -f ${service}

.PHONY: ps
ps:  ## Show the project's status
	docker compose -p ${project} ps

.PHONY: build
build:  ## Build the project's images
	docker compose -p ${project} build --no-cache

.PHONY: start-cleaned
start-cleaned: down build start  ## Clean all resources before start the project, execute down build start

.PHONY: shell
shell:  ## Enter in the container shell service=SERVICE_NAME, default core
	docker compose -p ${project} exec ${service} sh

.PHONY: install-package-in-container
install-package-in-container:  ## In the container install a package and update requirements.txt file, args: package=PACKEGE_NAME and service=SERVICE_NAME, default core
	docker compose -p ${project} exec ${service} pip install ${package}
	docker compose -p ${project} exec ${service} pip freeze > apps/core/requirements.txt

.PHONY: update-reuirements
update-reuirements:  ## update requirements.txt file, args: package=PACKEGE_NAME and service=SERVICE_NAME, default core
	docker compose -p ${project} exec ${service} pip freeze > apps/core/requirements.txt

.PHONY: add
add: start install-package-in-container build  ## Like install-package-in-container but install and build again the container, args: package=PACKEGE_NAME and service=SERVICE_NAME, default core

.PHONY: deps
deps:  ## Install reuirements.txt deps for container, args: service=SERVICE_NAME, default core
	docker compose -p ${project} exec ${service} pip install -r requirements.txt

.PHONY: show-deps
show-deps:  ## Show installed packages for container, args: service=SERVICE_NAME, default core
	docker compose -p ${project} exec ${service} pip freeze

.PHONY: setup
setup:	## Setup dev environment for your editor linter
	pip install -r ./apps/core/requirements.txt

.PHONY: run-test
run-test:	## Run tests for container, args: service=SERVICE_NAME, default core
	docker compose -p ${project} exec --workdir /opt/deploy/app ${service} coverage run --source=app -m pytest

# DB COMMANDS
.PHONY: create-migration
create-migration:	## Create db migration with message, args: message=MIGRATION_NAME and service=SERVICE_NAME, default core
	docker compose -p ${project} exec ${service} alembic revision --autogenerate -m "${message}"

.PHONY: apply-migration
apply-migration:	## Perform db migration, args: service=SERVICE_NAME, default core
	docker compose -p ${project} exec ${service} alembic upgrade head

# UTILS COMMANDS
.PHONY: lint
lint:
	docker-compose -p ${project} exec ${service} pylint apps/**/*.py

.PHONY: commit-hash
commit-hash:	## Print current commit hash
	@echo $(COMMIT_HASH)

# DEPLOY
.PHONY: build-release
build-release: 	## Prepare release image
	docker build -f apps/${service}/Dockerfile.prod --target release -t local/${service}:${COMMIT_HASH} .

