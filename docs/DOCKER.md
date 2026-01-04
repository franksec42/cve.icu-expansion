# CVE.ICU Docker Deployment

Run CVE.ICU in a container with automatic hourly data updates and local folder synchronization.

## Features

- **Automatic Updates**: Fetches and processes new CVE data every hour (configurable)
- **Startup Recovery**: Catches up on missed updates when container restarts
- **Local Sync**: Output files synchronized to your local `web/` folder
- **Persistent Cache**: Downloaded data cached locally for faster rebuilds
- **Health Monitoring**: Built-in health checks and logging

## Quick Start

```bash
# Build and run (one command)
make docker

# Or step by step:
make docker-build
make docker-run
```

The site will be available at **http://localhost:8090**

## Docker Commands

| Command | Description |
|---------|-------------|
| `make docker` | Build and run container |
| `make docker-build` | Build Docker image only |
| `make docker-run` | Run container (detached) |
| `make docker-up` | Run container with logs |
| `make docker-stop` | Stop container |
| `make docker-logs` | View container logs |
| `make docker-shell` | Shell into container |
| `make docker-update` | Trigger manual update |
| `make docker-rebuild` | Full rebuild in container |
| `make docker-clean` | Remove Docker resources |

## Configuration

### Environment Variables

Set these in `docker-compose.yml` or via command line:

| Variable | Default | Description |
|----------|---------|-------------|
| `UPDATE_INTERVAL` | `3600` | Update interval in seconds (1 hour) |
| `WEB_PORT` | `8090` | Web server port |
| `TZ` | `UTC` | Timezone for logs |

### Volume Mounts

| Container Path | Local Path | Purpose |
|----------------|------------|---------|
| `/app/web` | `./web` | Generated HTML & JSON output |
| `/app/data/cache` | `./data/cache` | Downloaded CVE data cache |
| `/var/log/cveicu` | `./logs` | Build and server logs |

## Usage Examples

### Run with Custom Update Interval (30 minutes)

```bash
docker-compose run -e UPDATE_INTERVAL=1800 cveicu
```

### Run with Different Port

```bash
docker-compose run -e WEB_PORT=3000 -p 3000:3000 cveicu
```

### Manual Build Only (no server)

```bash
docker-compose run --rm cveicu build full
```

### Quick Template Rebuild

```bash
docker-compose run --rm cveicu build quick
```

### Access Container Shell

```bash
make docker-shell
# or
docker-compose exec cveicu /bin/bash
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Container                      │
│  ┌─────────────────────────────────────────────────┐    │
│  │              supervisord                         │    │
│  │  ┌─────────────────┐  ┌───────────────────┐    │    │
│  │  │   Web Server    │  │    Scheduler      │    │    │
│  │  │  (port 8090)    │  │ (hourly updates)  │    │    │
│  │  └────────┬────────┘  └─────────┬─────────┘    │    │
│  └───────────┼─────────────────────┼──────────────┘    │
│              │                     │                    │
│  ┌───────────▼─────────────────────▼──────────────┐    │
│  │              /app/web (output)                  │    │
│  │              /app/data/cache (cached data)     │    │
│  └────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────┘
                         │ Volume Mounts
                         ▼
    ┌────────────────────────────────────────────────┐
    │                 Local Filesystem                │
    │  ./web/         - Generated site files          │
    │  ./data/cache/  - CVE data cache               │
    │  ./logs/        - Container logs               │
    └────────────────────────────────────────────────┘
```

## Startup Behavior

1. **Container starts** → Checks last build time
2. **If data is stale** (> UPDATE_INTERVAL) → Runs full build
3. **If data is fresh** → Runs quick template rebuild only
4. **Starts web server** on configured port
5. **Starts scheduler** for hourly updates

This means:
- First run: Full data download and processing (~5-10 minutes)
- Subsequent runs: Quick start if within update interval
- Interruption recovery: Automatic catch-up on restart

## Logs

View logs in real-time:
```bash
# All logs
make docker-logs

# Build logs only
tail -f logs/build.log

# Scheduler logs
tail -f logs/scheduler.out.log

# Web server logs
tail -f logs/webserver.out.log
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker-compose logs
```

### Build fails

1. Check disk space
2. Check network connectivity (NVD API access)
3. View detailed logs: `cat logs/build.log`

### Data not updating

1. Check scheduler is running: `docker-compose exec cveicu supervisorctl status`
2. Manually trigger: `make docker-update`
3. Check UPDATE_INTERVAL setting

### Port already in use

Change port in `docker-compose.yml`:
```yaml
ports:
  - "8091:8090"  # Use different local port
```

## Production Deployment

For production, consider:

1. **Use a reverse proxy** (nginx, traefik) for HTTPS
2. **Set resource limits** in docker-compose.yml
3. **Configure log rotation** for long-running containers
4. **Use Docker secrets** for any sensitive configuration
5. **Set up monitoring** (Prometheus, Grafana)

Example nginx proxy config:
```nginx
server {
    listen 443 ssl;
    server_name cve.example.com;
    
    location / {
        proxy_pass http://localhost:8090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Development Mode

For development with live template editing:

```yaml
# In docker-compose.yml, uncomment:
volumes:
  - ./templates:/app/templates:ro
```

Then templates will be read from your local folder. Run `make docker-quick` to rebuild after changes.

