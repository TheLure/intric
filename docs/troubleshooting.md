# Intric Troubleshooting Guide

## TLDR
- **Check Logs**: Use `docker-compose logs <service_name>` to identify errors
- **Verify Configuration**: Ensure environment variables are set correctly
- **Database Issues**: Check connections with `docker-compose exec db psql -U postgres`
- **Network Problems**: Verify containers can communicate with each other
- **Common Fixes**: Most issues can be resolved by checking container status, logs, and config files

This guide provides solutions for common issues encountered when deploying, developing, or using the Intric platform.

## Table of Contents
- [Deployment Issues](#deployment-issues)
- [Docker Issues](#docker-issues)
- [Database Issues](#database-issues)
- [Network Issues](#network-issues)
- [Authentication Issues](#authentication-issues)
- [LLM Integration Issues](#llm-integration-issues)
- [Frontend Issues](#frontend-issues)
- [Backend Issues](#backend-issues)
- [Performance Issues](#performance-issues)
- [Common Error Messages](#common-error-messages)
- [Getting Help](#getting-help)

## Deployment Issues

### Container Startup Failures

**Symptoms:**
- Containers exit immediately after starting
- Services show as "Exited" in `docker-compose ps`

**Possible Solutions:**
1. Check container logs:
   ```bash
   docker-compose logs <service_name>
   ```

2. Verify environment variables:
   ```bash
   docker-compose config
   ```

3. Ensure database initialization has been run:
   ```bash
   docker-compose --profile init up db-init
   ```

4. Check disk space:
   ```bash
   df -h
   ```

### Missing or Incorrect Environment Variables

**Symptoms:**
- Services fail with configuration errors
- "Key not found" or "Missing required configuration" errors

**Possible Solutions:**
1. Verify your `.env` file exists and contains all required variables
2. Compare your `.env` file with `.env.example`
3. Check for typos in variable names
4. Ensure sensitive values are properly escaped

### Image Pull Failures

**Symptoms:**
- "Error pulling image" messages
- Authentication errors with Docker registry

**Possible Solutions:**
1. Verify registry authentication:
   ```bash
   docker login ${NEXUS_REGISTRY}
   ```

2. Check image tag exists:
   ```bash
   docker pull ${NEXUS_REGISTRY}/intric/backend:${IMAGE_TAG}
   ```

3. Ensure proper network connectivity to the registry

4. Verify registry URL is correct in `.env` file

## Docker Issues

### Volume Permission Issues

**Symptoms:**
- Permission denied errors in logs
- Services unable to write to volumes

**Possible Solutions:**
1. Check ownership of volume directories:
   ```bash
   ls -la /path/to/docker/volumes
   ```

2. Adjust permissions:
   ```bash
   sudo chown -R 1000:1000 /path/to/docker/volumes
   ```

3. Use explicit volume configurations in docker-compose.yml:
   ```yaml
   volumes:
     postgres_data:
       driver: local
       driver_opts:
         type: none
         device: /path/to/data
         o: bind
   ```

### Resource Constraints

**Symptoms:**
- Services are slow or crash unexpectedly
- Out of memory errors

**Possible Solutions:**
1. Check Docker resource usage:
   ```bash
   docker stats
   ```

2. Increase allocated resources in Docker Desktop (if using)

3. Configure resource limits in docker-compose.yml:
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

### Network Conflicts

**Symptoms:**
- Port binding errors
- Services unable to communicate

**Possible Solutions:**
1. Check for port conflicts:
   ```bash
   sudo lsof -i :3000
   sudo lsof -i :8123
   ```

2. Change port mappings in docker-compose.yml:
   ```yaml
   services:
     frontend:
       ports:
         - "3001:3000"  # Change 3001 to an unused port
   ```

3. Use a different network name in docker-compose.yml if there are network namespace conflicts

## Database Issues

### Connection Failures

**Symptoms:**
- "Could not connect to database" errors
- Backend service restarts repeatedly

**Possible Solutions:**
1. Verify database service is running:
   ```bash
   docker-compose ps db
   ```

2. Check database logs:
   ```bash
   docker-compose logs db
   ```

3. Ensure database credentials are correct in `.env` file

4. Try connecting manually:
   ```bash
   docker-compose exec db psql -U postgres
   ```

### Migration Errors

**Symptoms:**
- Database schema errors
- "Relation does not exist" errors

**Possible Solutions:**
1. Run database initialization:
   ```bash
   docker-compose --profile init up db-init
   ```

2. Check migration logs:
   ```bash
   docker-compose logs db-init
   ```

3. For development, try resetting the database:
   ```bash
   docker-compose down -v  # WARNING: This deletes all data!
   docker-compose up -d db
   # Then run initialization again
   ```

### pgvector Issues

**Symptoms:**
- Vector search not working
- "Extension not available" errors

**Possible Solutions:**
1. Verify pgvector extension is installed:
   ```sql
   SELECT * FROM pg_extension WHERE extname = 'vector';
   ```

2. Install the extension manually if needed:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. Ensure you're using PostgreSQL 13 or higher with pgvector extension

4. Check vector dimensions match in your application and database:
   ```sql
   SELECT column_name, data_type 
   FROM information_schema.columns 
   WHERE table_name = 'embeddings';
   ```

## Network Issues

### Internal Service Communication

**Symptoms:**
- Services can't communicate with each other
- "Connection refused" errors

**Possible Solutions:**
1. Check Docker network:
   ```bash
   docker network inspect intric_default
   ```

2. Verify service names are used as hostnames:
   ```bash
   docker-compose exec backend ping redis
   ```

3. Ensure all services are on the same Docker network

### External Access Issues

**Symptoms:**
- Can't access frontend from browser
- API requests fail from external clients

**Possible Solutions:**
1. Check port forwarding:
   ```bash
   docker-compose ps
   ```

2. Verify firewall settings:
   ```bash
   sudo ufw status
   ```

3. If using a reverse proxy, check its configuration

4. Ensure `SERVICE_FQDN_FRONTEND` is set correctly in production

5. Check if your service is listening on the correct interface:
   ```bash
   docker-compose exec frontend netstat -tulpn
   ```

## Authentication Issues

### JWT Token Problems

**Symptoms:**
- "Invalid token" errors
- Users get logged out unexpectedly

**Possible Solutions:**
1. Verify `JWT_SECRET` is set and consistent across restarts

2. Check token expiration time (`JWT_EXPIRY_TIME`) is appropriate

3. Ensure clock synchronization between server and clients

4. Verify JWT configuration with a tool like jwt.io

5. Check browser console for CORS issues with authentication headers

### Login Failures

**Symptoms:**
- Users unable to log in
- Authentication errors in logs

**Possible Solutions:**
1. Check credentials in development setup:
   ```
   Default credentials: user@example.com / Password1!
   ```

2. Verify authentication flow in logs:
   ```bash
   docker-compose logs backend | grep -i auth
   ```

3. For MobilityGuard integration, check OIDC configuration values

4. Verify that the authentication endpoint is responding correctly:
   ```bash
   curl -X POST http://localhost:8123/api/v1/auth/login -d '{"email":"user@example.com","password":"Password1!"}'
   ```

## LLM Integration Issues

### API Key Problems

**Symptoms:**
- "Invalid API key" errors
- LLM responses failing

**Possible Solutions:**
1. Verify API keys are set correctly in `.env` file

2. Check API key validity with the provider's tools

3. Ensure you have sufficient quota/credits with the LLM provider

4. Check for any IP restrictions on API keys

5. Verify that LLM API keys have been loaded by the application:
   ```bash
   docker-compose exec backend python -c "import os; print('OPENAI_API_KEY exists:', bool(os.environ.get('OPENAI_API_KEY')))"
   ```

### Response Timeouts

**Symptoms:**
- LLM responses take too long or time out
- Incomplete responses

**Possible Solutions:**
1. Increase timeout settings in the application

2. Check network connectivity to LLM provider

3. Verify outbound internet access is available for backend container

4. Consider reducing model complexity or prompt length

5. Try a different LLM provider to rule out provider-specific issues

### Content Filtering Issues

**Symptoms:**
- Responses are blocked by LLM provider filters
- "Content policy violation" errors

**Possible Solutions:**
1. Review prompt templates for potentially problematic content

2. Consider using a different LLM provider to rule out provider-specific filtering issues

3. Check the prompt structure to ensure it follows provider guidelines

4. If permitted by your provider, check their documentation for any available content filter configuration options

## Frontend Issues

### UI Rendering Problems

**Symptoms:**
- Components not rendering correctly
- Visual glitches or styling issues

**Possible Solutions:**
1. Clear browser cache and reload

2. Check browser console for JavaScript errors

3. Verify CSS is loading properly

4. Test in a different browser to isolate the issue

5. Check if all frontend dependencies are loading correctly:
   ```bash
   docker-compose exec frontend ls -la /usr/share/nginx/html
   ```

### State Management Issues

**Symptoms:**
- UI gets out of sync with backend
- Unexpected behavior after user actions

**Possible Solutions:**
1. Check Svelte store implementations

2. Verify API responses in Network tab

3. Review component lifecycle management

4. Add more detailed logging to identify where state becomes inconsistent

### Performance Problems

**Symptoms:**
- Slow UI rendering
- Delayed responses to user interactions

**Possible Solutions:**
1. Check for memory leaks in browser dev tools

2. Review component re-rendering patterns

3. Consider implementing pagination for large datasets

4. Optimize frontend bundle size

5. Use performance profiling tools to identify bottlenecks:
   ```javascript
   console.time('operation');
   // Code to measure
   console.timeEnd('operation');
   ```

## Backend Issues

### API Endpoint Failures

**Symptoms:**
- Specific API endpoints return errors
- Unexpected response formats

**Possible Solutions:**
1. Check backend logs for detailed error messages:
   ```bash
   docker-compose logs backend
   ```

2. Review API route implementation for that endpoint

3. Verify request format matches expected schema

4. Test endpoint directly with curl or Postman:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8123/api/v1/endpoint
   ```

### Worker Task Failures

**Symptoms:**
- Background tasks fail or get stuck
- Document processing doesn't complete

**Possible Solutions:**
1. Check worker logs:
   ```bash
   docker-compose logs worker
   ```

2. Verify Redis connection:
   ```bash
   docker-compose exec redis redis-cli ping
   ```

3. Check for resource constraints affecting worker

4. Ensure task queue is processing correctly:
   ```bash
   docker-compose exec redis redis-cli LLEN arq:queue
   ```

5. Try requeuing stuck tasks:
   ```bash
   docker-compose exec redis redis-cli DEL arq:job:YOUR_JOB_ID
   ```

### Domain Logic Issues

**Symptoms:**
- Unexpected application behavior
- Business rules not being enforced correctly

**Possible Solutions:**
1. Check domain entity implementations

2. Verify service layer logic

3. Add more detailed logging for domain operations

4. Review the affected domain's test coverage

## Performance Issues

### Slow Query Performance

**Symptoms:**
- Database queries take too long
- API responses are delayed

**Possible Solutions:**
1. Check database indexes:
   ```sql
   SELECT * FROM pg_indexes;
   ```

2. Review query performance with EXPLAIN:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM table WHERE condition;
   ```

3. Consider optimizing vector search parameters:
   ```sql
   ALTER INDEX embedding_idx SET (probes = 10);
   ```

4. Monitor database connection pool usage

5. Check for N+1 query patterns in ORM code

### Memory Usage Problems

**Symptoms:**
- Services use excessive memory
- Out of memory errors

**Possible Solutions:**
1. Monitor memory usage:
   ```bash
   docker stats
   ```

2. Check for memory leaks in backend code

3. Optimize batch processing sizes

4. Adjust PostgreSQL memory settings:
   ```
   shared_buffers
   work_mem
   effective_cache_size
   ```

### High CPU Usage

**Symptoms:**
- High CPU utilization
- Slow overall system response

**Possible Solutions:**
1. Monitor CPU usage per container:
   ```bash
   docker stats
   ```

2. Identify CPU-intensive operations in logs

3. Consider scaling horizontally for better load distribution

4. Review algorithms for optimization opportunities

5. Profile Python code to find CPU-intensive operations:
   ```python
   import cProfile
   cProfile.run('function_to_profile()')
   ```

## Common Error Messages

### "No such container"

**Possible Solutions:**
1. Check if all containers are running:
   ```bash
   docker-compose ps
   ```

2. Rebuild and restart containers:
   ```bash
   docker-compose up -d --build
   ```

### "Connection refused"

**Possible Solutions:**
1. Verify the service is running
2. Check hostname and port are correct
3. Ensure network connectivity between services
4. Check if the service is listening on the expected interface (not just localhost)

### "Permission denied"

**Possible Solutions:**
1. Check file and directory permissions
2. Verify container user has appropriate access
3. Review volume mount configurations
4. Use Docker user namespace mapping for persistent volume access

### "Out of memory"

**Possible Solutions:**
1. Increase available memory for Docker
2. Review memory-intensive operations
3. Consider memory limitations in configuration
4. Implement appropriate memory limits in docker-compose.yml
5. Add swap space if necessary (though not recommended for production)

### "Database is being accessed by other users"

**Possible Solutions:**
1. Check for connections to the database:
   ```bash
   docker-compose exec db psql -U postgres -c "SELECT * FROM pg_stat_activity;"
   ```

2. Terminate blocking connections if necessary:
   ```bash
   docker-compose exec db psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'postgres' AND pid <> pg_backend_pid();"
   ```

### "vector_eq_op_procedure doesn't exist"

**Possible Solutions:**
1. This typically indicates a pgvector installation issue
2. Verify pgvector extension is installed correctly:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Ensure you're using a compatible PostgreSQL version with pgvector

## Getting Help

If you're still experiencing issues after trying these troubleshooting steps:

1. Check GitHub issues for similar problems
2. Join the community forum (email [digitalisering@sundsvall.se](mailto:digitalisering@sundsvall.se))
3. Collect detailed logs and error messages to help with diagnosis:
   ```bash
   docker-compose logs > intric-logs.txt
   ```
4. Prepare a minimal reproduction case if possible
5. Include your environment details when asking for help:
   ```bash
   docker version
   docker-compose version
   docker info
   ```