#!/bin/sh
set -e

# Inject BACKEND_URL into nginx config at container startup
envsubst '${BACKEND_URL}' \
    < /etc/nginx/templates/nginx.conf.template \
    > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
