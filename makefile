init:
	pip install -r requirements.txt

build:
	docker-compose build
	docker-compose -f docker-compose.yml up --build

up:
	docker-compose -f docker-compose.yml up -d

down:
	docker-compose -f docker-compose.yml down

restart:
	docker-compose -f docker-compose.yml restart

logs:
	docker-compose -f docker-compose.yaml logs -f
