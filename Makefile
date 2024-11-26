export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

all: down build up test


sh:
	docker-compose -f docker-compose.yml ps -a

build:
	docker-compose -f docker-compose.yml build

up:
	docker-compose -f docker-compose.yml up -d --build

down:
	docker-compose -f docker-compose.yml down --remove-orphans

restart:
	$(MAKE) down
	$(MAKE) up

test: up
	docker-compose -f docker-compose.yml run --rm --no-deps --entrypoint=pytest app /tests/core /tests/modules

# unit-tests:
# 	docker-compose run --rm --no-deps --entrypoint=pytest app /tests/unit

# integration-tests: up
# 	docker-compose run --rm --no-deps --entrypoint=pytest app /tests/integration

# e2e-tests: up
# 	docker-compose run --rm --no-deps --entrypoint=pytest app /tests/e2e

logs:
	docker-compose logs app | tail -100

black:
	black -l 86 $$(find * -name '*.py')

# migrate:
#     alembic revision -m 

upgrade:
	alembic upgrade head
