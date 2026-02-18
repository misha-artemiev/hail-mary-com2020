CONTAINER_ENGINE := $(shell command -v podman 2> /dev/null || command -v docker 2> /dev/null)

ifeq ($(CONTAINER_ENGINE),)
    $(error "no container runtime (podman or docker) found")
endif

ifeq ($(notdir $(CONTAINER_ENGINE)),podman)
    COMPOSE := $(CONTAINER_ENGINE) compose
else
    COMPOSE := $(CONTAINER_ENGINE) compose
endif

up:
	@$(COMPOSE) -f ./docker-compose.yaml up --build

up-detach:
	@$(COMPOSE) -f ./docker-compose.yaml up --build --detach

up-built:
	@$(COMPOSE) -f ./docker-compose.yaml up

up-built-detach:
	@$(COMPOSE) -f ./docker-compose.yaml up --detach

down:
	@$(COMPOSE) -f ./docker-compose.yaml down
