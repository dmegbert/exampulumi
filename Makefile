ENV_NAME ?= dev
SERVICE_NAME = exampulumi
BRANCH_NAME ?= $(shell git rev-parse --abbrev-ref HEAD)

create-migration:
ifdef message
	cd backend; \
	alembic revision --autogenerate -m "$(message)"
else
	@printf 'Use "make create-migration and include message: make create-migration message="add user table"\n'
endif

run-migration:
	cd backend; \
	alembic upgrade head

undo-migration:
	cd backend; \
	alembic downgrade -1
