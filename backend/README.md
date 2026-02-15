# backend
## run
### install dependencies
```bash
pip install "."
```
### start
```bash
make run
```

## development
### install dependencies
#### pip
```bash
pip install -e ".[dev]"
```
#### sqlc
[sqlc install docs](https://docs.sqlc.dev/en/latest/overview/install.html)

### regen
#### docs
```bash
make docs
```
#### queries
```bash
make sql
```
### syntax checks
#### soft check (no changes)
```bash
make check
```
#### hard check (applies changes)
```bash
make check-apply
```
## environmental variables (.env)
```dotenv
HOST_HOST="localhost"
HOST_PORT=8080
HOST_NAME="hail mary"
HOST_FORWARD_FROM="*"

DATABASE_HOST="noxbound.com"
DATABASE_PORT=5432
DATABASE_DATABASE="hail-mary"
DATABASE_USERNAME="hail-mary"
DATABASE_PASSWORD="<password>"
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

AUTH_TOKEN_EXPARATION=360
```

## Database management
```
make init-db
```
