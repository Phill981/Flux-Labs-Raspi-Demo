# Patient Vitals API - Deployment Guide

## Docker Deployment

This application is containerized and ready for deployment on Coolify or any Docker-compatible platform.

### Files Included

- `Dockerfile` - Production-ready container configuration
- `docker-compose.yml` - Local development setup
- `start.sh` - Production startup script
- `.dockerignore` - Optimized build context
- `requirements.txt` - Python dependencies

### Coolify Deployment

1. **Connect Repository**: Link your Git repository to Coolify
2. **Build Settings**: 
   - Dockerfile path: `./Dockerfile`
   - Build context: `.`
3. **Environment Variables**: None required (all configuration is in code)
4. **Port**: 8000 (automatically exposed)
5. **Health Check**: Built-in health check at `/`

### Local Testing

```bash
# Build the image
docker build -t patient-vitals-api .

# Run locally
docker run -p 8000:8000 -v $(pwd)/patients_data.json:/app/patients_data.json:ro patient-vitals-api

# Or use docker-compose
docker-compose up --build
```

### API Endpoints

- `GET /` - Health check and basic info
- `GET /vitals/current` - Current vital data
- `GET /vitals/previous` - Previous vital data (snapshot)
- `GET /vitals/snapshot` - Saved snapshot data
- `GET /vitals/save` - Save current vitals as snapshot
- `GET /vitals/increment` - Advance timeline
- `GET /vitals/status` - System status
- `GET /vitals/snapshot/info` - Snapshot information

### Performance Features

- **Streaming JSON Parser**: Handles large 135MB+ JSON files efficiently
- **Memory Optimized**: Uses ~5-10MB RAM instead of 135MB+
- **Caching**: LRU cache for frequently accessed data
- **Health Checks**: Built-in monitoring

### Data Requirements

The application expects `patients_data.json` to be available in the container. This file should contain the patient vital data in the expected format.

### Security Features

- Non-root user execution
- Minimal attack surface
- Health check monitoring
- Proper error handling

### Monitoring

The application includes:
- Health check endpoint at `/`
- Structured logging
- Performance metrics
- Error tracking
