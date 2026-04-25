.PHONY: dev dev-backend dev-frontend deploy teardown seed

dev-backend:
	cd backend && uvicorn main:app --reload --port 8080 --env-file .env

dev-frontend:
	cd frontend && npm run dev

dev:
	./scripts/dev.sh

deploy:
	./scripts/deploy.sh

teardown:
	./scripts/teardown.sh

seed:
	./scripts/seed.sh
