docker build -t agentish_street-fighter_mcp_trainer:latest \
  -f services/mcp_trainer/Dockerfile \
  .

docker build -t agentish_street-fighter_mcp_arena:latest \
  -f services/mcp_arena/Dockerfile \
  .

docker build -t agentish_street-fighter_datastore:latest \
  -f services/datastore/Dockerfile \
  .

# THEN run compose
docker compose up --build