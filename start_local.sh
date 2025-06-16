#!/bin/bash

# Eliminar cualquier contenedor anterior de Redis detenido
docker rm -f redis-ainomics 2>/dev/null

# Iniciar Redis sin contraseña
docker run --rm -d \
  --name redis-ainomics \
  -v "$HOME/docker-volumes/redis-ainomics:/data" \
  -p 6379:6379 \
  redis:7 \
  redis-server --appendonly yes

# Iniciar Redis Commander sin contraseña
docker run --rm -d \
  --name redis-commander \
  --link redis-ainomics \
  -e REDIS_HOSTS="local:redis-ainomics:6379" \
  -e HTTP_USER=admin \
  -e HTTP_PASSWORD=admin123 \
  -p 8081:8081 \
  rediscommander/redis-commander:latest
