.PHONY: dev dev-backend dev-frontend deploy teardown seed seed-data seed-data-fresh build-index upload-index update-kb

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

seed-data:
	python scripts/seed_data.py

seed-data-fresh:
	python scripts/seed_data.py --clear

build-index:
	python backend/scripts/build_faiss_index.py

upload-index:
	@echo "Requires S3_BUCKET env var. Get it from CDK output FaissIndexBucketName."
	python backend/scripts/upload_index_to_s3.py

update-kb: build-index upload-index
