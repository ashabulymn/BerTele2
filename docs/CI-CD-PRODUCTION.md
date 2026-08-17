# BerTele2 CI/CD Production Setup

This repository uses GitHub Actions for CI and SSH for production deployment.

## Flow

1. Pull requests to `main` run CI.
2. CI installs Python dependencies, compiles the backend, builds the dashboard, validates Compose, and builds the Docker image for `linux/arm64`.
3. Only a push to `main` can run the production deploy job.
4. GitHub connects to the VPS over SSH.
5. The SSH account can only sudo the fixed `/usr/local/sbin/bertele2-deploy` command.
6. The deploy helper refuses to run if tracked local changes exist.
7. It fetches the exact pushed commit, validates Compose, builds the service, restarts it, and checks `http://127.0.0.1:8000/api/v1/health`.
8. If build/start/health fails, the previous Docker image is restored when available.

## Production prerequisites

Install the deployment helper on the VPS as root. Run these commands from the BerTele2 repository working tree after this CI/CD branch has been merged into `main`:

```bash
cd /etc/dokploy/compose/apps-bertele2-qbabwx/code
install -m 0755 ops/bertele2-deploy.sh /usr/local/sbin/bertele2-deploy
```

Create a dedicated deployment user:

```bash
id bertele2-deploy >/dev/null 2>&1 || useradd --create-home --shell /bin/bash bertele2-deploy
install -d -m 0700 -o bertele2-deploy -g bertele2-deploy /home/bertele2-deploy/.ssh
```

Add the GitHub Actions public key to `/home/bertele2-deploy/.ssh/authorized_keys` and set:

```bash
chown bertele2-deploy:bertele2-deploy /home/bertele2-deploy/.ssh/authorized_keys
chmod 0600 /home/bertele2-deploy/.ssh/authorized_keys
```

Allow only the deployment helper through sudo:

```bash
cat >/etc/sudoers.d/bertele2-deploy <<'EOF'
bertele2-deploy ALL=(root) NOPASSWD: /usr/local/sbin/bertele2-deploy *
EOF
chmod 0440 /etc/sudoers.d/bertele2-deploy
visudo -cf /etc/sudoers.d/bertele2-deploy
```

The helper is hard-coded to `/etc/dokploy/compose/apps-bertele2-qbabwx/code`, so the SSH user cannot use this sudo rule to deploy another project.

## GitHub Actions secrets

Create these secrets in the repository's `production` environment:

- `DEPLOY_HOST` — VPS hostname or IP address.
- `DEPLOY_USER` — `bertele2-deploy`.
- `DEPLOY_SSH_KEY` — the private Ed25519 key used only by GitHub Actions.
- `DEPLOY_KNOWN_HOSTS` — the exact SSH host-key line for the VPS.

The production environment should require approval before deployment if you want a manual approval gate.

## Generate a dedicated SSH key

On a trusted machine:

```bash
ssh-keygen -t ed25519 -C 'github-actions-bertele2' -f ./bertele2_github_actions_ed25519
```

Put the contents of `bertele2_github_actions_ed25519.pub` into the deploy user's `authorized_keys`. Put the private key into GitHub as `DEPLOY_SSH_KEY`.

Never commit the private key.

## Get the pinned host key

From a trusted network, verify the server fingerprint independently and then capture the known-host entry:

```bash
ssh-keyscan -t ed25519 YOUR_SERVER_HOST
```

Only after verifying the fingerprint, store the output in `DEPLOY_KNOWN_HOSTS`.

## Important production state

The current Dokploy working tree may contain local tracked changes. The deployment helper intentionally refuses to deploy while those changes exist. Commit/push the intended BerTele2 changes first; do not use `git reset --hard` manually just to make CI/CD pass.

Production `.env` stays on the VPS and is not copied to GitHub. The repository `.gitignore` must continue to exclude `.env` and other credentials.
