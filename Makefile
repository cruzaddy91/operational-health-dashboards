.PHONY: demo up down logs test fmt

demo: up
	@echo ""
	@echo "Stack is up. Open:"
	@echo "  Grafana:    http://localhost:3000  (admin / admin)"
	@echo "  Prometheus: http://localhost:9090"
	@echo "  Emitter:    http://localhost:9100/metrics"
	@echo ""
	@echo "Stop with: make down"

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=50

test:
	python -m pytest tests/ -v
