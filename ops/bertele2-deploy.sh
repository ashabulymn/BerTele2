#!/usr/bin/env bash
set -Eeuo pipefail

DEPLOY_SHA="${1:?missing commit SHA}"
PROJECT_DIR="${2:?missing project directory}"
EXPECTED_BRANCH="main"
COMPOSE_PROJECT="apps-bertele2-qbabwx"
SERVICE="bertele2"
HEALTH_URL="http://127.0.0.1:8000/api/v1/health"
ROLLBACK_TAG="${COMPOSE_PROJECT}-${SERVICE}:rollback"
PREVIOUS_SHA=""
PREVIOUS_IMAGE_ID=""
ROLLING_BACK=0

log() { printf '[bertele2-deploy] %s\n' "$*"; }

rollback() {
  local code=$?
  [[ "$ROLLING_BACK" -eq 1 ]] && return "$code"
  ROLLING_BACK=1
  set +e
  log "Deployment failed (exit $code); attempting rollback"

  if [[ -n "$PREVIOUS_IMAGE_ID" ]]; then
    docker image tag "$ROLLBACK_TAG" "${COMPOSE_PROJECT}-${SERVICE}" 2>/dev/null || true
    docker compose -p "$COMPOSE_PROJECT" -f docker-compose.yml up -d --no-build "$SERVICE" || true
    sleep 3
    if curl -fsS --max-time 5 "$HEALTH_URL" >/tmp/bertele2-rollback-health.json 2>/dev/null; then
      log "Rollback restored a healthy service"
      cat /tmp/bertele2-rollback-health.json || true
    else
      log "WARNING: rollback container started but health check is still failing"
    fi
  else
    log "No previous image was available; image rollback is not possible"
  fi

  if [[ -n "$PREVIOUS_SHA" ]]; then
    git reset --hard "$PREVIOUS_SHA" >/dev/null 2>&1 || true
  fi
  return "$code"
}
trap rollback ERR

[[ "$(id -u)" -eq 0 ]] || { log 'ERROR: this script must run as root' >&2; exit 1; }
[[ -d "$PROJECT_DIR/.git" ]] || { log "ERROR: not a Git working tree: $PROJECT_DIR" >&2; exit 1; }
[[ -f "$PROJECT_DIR/docker-compose.yml" ]] || { log 'ERROR: docker-compose.yml not found' >&2; exit 1; }

cd "$PROJECT_DIR"

CURRENT_BRANCH="$(git branch --show-current)"
[[ "$CURRENT_BRANCH" == "$EXPECTED_BRANCH" ]] || { log "ERROR: expected branch $EXPECTED_BRANCH, found $CURRENT_BRANCH" >&2; exit 1; }

# Never destroy tracked local production edits.
if ! git diff --quiet || ! git diff --cached --quiet; then
  git status --short >&2 || true
  log 'ERROR: tracked local changes exist; refusing deployment' >&2
  exit 1
fi

log 'Fetching origin/main'
git fetch --prune origin main

REMOTE_SHA="$(git rev-parse origin/main)"
[[ "$REMOTE_SHA" == "$DEPLOY_SHA" ]] || { log "ERROR: requested SHA $DEPLOY_SHA is not origin/main ($REMOTE_SHA)" >&2; exit 1; }

PREVIOUS_SHA="$(git rev-parse HEAD)"
PREVIOUS_IMAGE_ID="$(docker inspect --format '{{.Image}}' "${COMPOSE_PROJECT}-${SERVICE}-1" 2>/dev/null || true)"
if [[ -z "$PREVIOUS_IMAGE_ID" ]]; then
  PREVIOUS_IMAGE_ID="$(docker inspect --format '{{.Image}}' "${COMPOSE_PROJECT}-${SERVICE}" 2>/dev/null || true)"
fi

if [[ -n "$PREVIOUS_IMAGE_ID" ]]; then
  log "Saving rollback image $PREVIOUS_IMAGE_ID"
  docker image tag "$PREVIOUS_IMAGE_ID" "$ROLLBACK_TAG"
fi

log "Deploying commit $DEPLOY_SHA"
git reset --hard "$DEPLOY_SHA"

log 'Validating Compose configuration'
docker compose -p "$COMPOSE_PROJECT" -f docker-compose.yml config --quiet

log "Building $SERVICE"
docker compose -p "$COMPOSE_PROJECT" -f docker-compose.yml build --pull "$SERVICE"

log "Starting $SERVICE"
docker compose -p "$COMPOSE_PROJECT" -f docker-compose.yml up -d --no-build "$SERVICE"

log 'Waiting for health endpoint'
healthy=0
for attempt in $(seq 1 30); do
  if curl -fsS --max-time 5 "$HEALTH_URL" >/tmp/bertele2-health.json 2>/dev/null; then
    healthy=1
    break
  fi
  sleep 2
done

if [[ "$healthy" -ne 1 ]]; then
  log 'ERROR: health check failed' >&2
  exit 1
fi

log 'Deployment healthy'
cat /tmp/bertele2-health.json || true
