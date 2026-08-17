#!/usr/bin/env bash
set -Eeuo pipefail

# Production deployment helper for the BerTele2 Dokploy Compose project.
# Arguments:
#   1. exact Git commit SHA to deploy
#   2. absolute Compose project path

DEPLOY_SHA="${1:?missing commit SHA}"
PROJECT_DIR="${2:?missing project directory}"
EXPECTED_BRANCH="main"
COMPOSE_PROJECT="apps-bertele2-qbabwx"
SERVICE="bertele2"
HEALTH_URL="http://127.0.0.1:8000/api/v1/health"
ROLLBACK_TAG="${COMPOSE_PROJECT}-${SERVICE}:rollback"

log() { printf '[bertele2-deploy] %s\n' "$*"; }
fail() { log "ERROR: $*" >&2; exit 1; }

[[ "$(id -u)" -eq 0 ]] || fail "this script must run as root"
[[ -d "$PROJECT_DIR/.git" ]] || fail "not a Git working tree: $PROJECT_DIR"
[[ -f "$PROJECT_DIR/docker-compose.yml" ]] || fail "docker-compose.yml not found"

cd "$PROJECT_DIR"

CURRENT_BRANCH="$(git branch --show-current)"
[[ "$CURRENT_BRANCH" == "$EXPECTED_BRANCH" ]] || fail "expected branch $EXPECTED_BRANCH, found $CURRENT_BRANCH"

# Never destroy uncommitted tracked production changes.
if ! git diff --quiet || ! git diff --cached --quiet; then
  git status --short >&2 || true
  fail "tracked local changes exist; refusing deployment"
fi

log "Fetching origin/main"
git fetch --prune origin main

REMOTE_SHA="$(git rev-parse origin/main)"
[[ "$REMOTE_SHA" == "$DEPLOY_SHA" ]] || fail "requested SHA $DEPLOY_SHA is not origin/main ($REMOTE_SHA)"

PREVIOUS_IMAGE_ID="$(docker inspect --format '{{.Image}}' "${COMPOSE_PROJECT}-${SERVICE}-1" 2>/dev/null || true)"
if [[ -z "$PREVIOUS_IMAGE_ID" ]]; then
  PREVIOUS_IMAGE_ID="$(docker inspect --format '{{.Image}}' "${COMPOSE_PROJECT}-${SERVICE}" 2>/dev/null || true)"
fi

if [[ -n "$PREVIOUS_IMAGE_ID" ]]; then
  log "Saving rollback image $PREVIOUS_IMAGE_ID"
  docker image tag "$PREVIOUS_IMAGE_ID" "$ROLLBACK_TAG"
fi

PREVIOUS_SHA="$(git rev-parse HEAD)"
log "Deploying commit $DEPLOY_SHA (previous $PREVIOUS_SHA)"
git reset --hard "$DEPLOY_SHA"

git clean -fd -e .env -e data/ -e '*.backup-*' || true

log "Validating Compose configuration"
docker compose -p "$COMPOSE_PROJECT" -f docker-compose.yml config --quiet

log "Building $SERVICE"
docker compose -p "$COMPOSE_PROJECT" -f docker-compose.yml build --pull "$SERVICE"

log "Starting $SERVICE"
docker compose -p "$COMPOSE_PROJECT" -f docker-compose.yml up -d --no-build "$SERVICE"

log "Waiting for health endpoint"
healthy=0
for attempt in $(seq 1 30); do
  if curl -fsS --max-time 5 "$HEALTH_URL" >/tmp/bertele2-health.json 2>/dev/null; then
    healthy=1
    break
  fi
  sleep 2
done

if [[ "$healthy" -eq 1 ]]; then
  log "Deployment healthy"
  cat /tmp/bertele2-health.json || true
  exit 0
fi

log "Health check failed; starting rollback"
if [[ -n "$PREVIOUS_IMAGE_ID" ]]; then
  docker image tag "$ROLLBACK_TAG" "${COMPOSE_PROJECT}-${SERVICE}"
  docker compose -p "$COMPOSE_PROJECT" -f docker-compose.yml up -d --no-build "$SERVICE" || true
  sleep 3
  if curl -fsS --max-time 5 "$HEALTH_URL" >/tmp/bertele2-rollback-health.json 2>/dev/null; then
    log "Rollback restored a healthy service"
  else
    log "WARNING: rollback container started but health check is still failing"
  fi
else
  log "No previous image was available; cannot perform image rollback"
fi

git reset --hard "$PREVIOUS_SHA" || true
exit 1
