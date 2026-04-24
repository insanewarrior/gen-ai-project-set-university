.PHONY: dev dev-backend dev-frontend deploy seed

dev-backend:
	cd backend && uvicorn main:app --reload --port 8080

dev-frontend:
	cd frontend && npm run dev

dev:
	./scripts/dev.sh

deploy:
	./scripts/deploy.sh

seed:
	./scripts/seed.sh
