# Deployment

## Docker (recommended for production)

```bash
# Build image
make docker-build

# Start full stack (app + Chroma + Redis + Postgres)
make docker-up

# Tail logs
docker-compose logs -f app

# Stop
make docker-down
```

Environment variables are read from `.env`. Copy `.env.example` to `.env` and fill in your keys.

## Kubernetes

Basic manifests in `kubernetes/`:

```bash
kubectl apply -f kubernetes/
kubectl get pods -n research-agent
```

Set API keys as Kubernetes Secrets:
```bash
kubectl create secret generic research-agent-secrets \
  --from-literal=ANTHROPIC_API_KEY=your_key \
  --from-literal=OPENAI_API_KEY=your_key \
  --from-literal=TAVILY_API_KEY=your_key
```

## Vector store

### Chroma (default — local dev)
No setup needed. Persists to `.chroma/` directory.

### pgvector (production)
1. Deploy Postgres 16 with pgvector extension
2. Create the database: `CREATE DATABASE research_agent;`
3. Install extension: `CREATE EXTENSION IF NOT EXISTS vector;`
4. Set `VECTOR_STORE_BACKEND=pgvector` and `DATABASE_URL=postgresql://...`

## Health checks

```
GET /health
```

Returns:
```json
{
  "status": "ok",
  "vector_store": {"backend": "chroma", "status": "ok"},
  "redis": {"status": "ok"},
  "llm": {"status": "ok", "key_prefix": "sk-ant-..."}
}
```

## Scaling

- The app is stateless — scale horizontally behind a load balancer
- Use Redis for result caching and conversation memory (shared across instances)
- Use pgvector (not Chroma) for multi-instance deployments
- Prometheus metrics endpoint: `GET /metrics` (requires `prometheus-fastapi-instrumentator`)
