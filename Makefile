run:
	docker-compose build && docker-compose up

test:
	docker exec main find . -name \*.pyc -delete  # Crutch: clearing cache before run
	docker exec main pytest
