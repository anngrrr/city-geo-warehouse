FROM postgres:15-alpine

# Copy initialization SQL to bootstrap schemas
COPY ./init.sql /docker-entrypoint-initdb.d/10-init.sql\n
