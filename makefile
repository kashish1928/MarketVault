# Download requirements.txt (recommend running this command in .venv)
init:
	pip install -r requirements.txt

# Activate .venv
activate:
	bash -c "source .venv/bin/activate && exec bash"

# Run this whenever there are changes to the dockerfile or docker-compose file
build:
	docker-compose build
	docker-compose -f docker-compose.yml up --build

# Run this before every session to start up the docker containers
up:
	docker-compose -f docker-compose.yml up -d

# Run this at the end of every session to stop the docker containers
down:
	docker-compose -f docker-compose.yml down

# Run this to restart docker containers
restart:
	docker-compose -f docker-compose.yml restart

# Run this to view docker container logs
logs:
	docker-compose -f docker-compose.yaml logs -f

# Run this to connect to postgres server using CLI
psql:
	psql -h localhost -p 5433 -U airflow -d stockdb
