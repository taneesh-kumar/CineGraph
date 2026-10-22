# CineGraph Docker Infrastructure

This directory provides documentation and helper references for CineGraph's containerized database infrastructure.

## Databases

1. **Neo4j Community Edition**
   - **Role**: Graph database storing entities (Movies, Actors, Directors, Genres, Users) and relationships (`:ACTED_IN`, `:DIRECTED`, `:RATED`, `:BELONGS_TO`).
   - **Protocol Ports**:
     - Web Browser Interface: `http://127.0.0.1:7474`
     - Bolt Binary Protocol: `bolt://127.0.0.1:7687`
   - **Data Volume**: `neo4j_data` -> `/data`
   - **Authentication**: `neo4j` user with password loaded securely from `.env` (`NEO4J_PASSWORD`).

2. **MonetDB Column Store**
   - **Role**: High-performance analytical columnar SQL database for aggregate statistics, ratings over time, genre distribution, and release-year trends.
   - **Protocol Port**:
     - MonetDB MAPI / SQL port: `127.0.0.1:50000`
   - **Data Volume**: `monetdb_data` -> `/var/monetdb5/dbfarm`
   - **Authentication**: Default system user `monetdb` with remote daemon management passphrase configured via `MDB_DAEMON_PASS` from `.env`.

## Managing Containers

### Start Databases
From the repository root:
```bash
# Start containers in detached mode
docker compose up -d
```

### Check Status & Logs
```bash
docker compose ps
docker compose logs -f
docker compose logs neo4j
docker compose logs monetdb
```

### Stop Databases (Preserving Data)
```bash
docker compose stop
# or
docker compose down
```
> **Note**: `docker compose down` removes containers and network, but **preserves** persisted Docker volumes (`neo4j_data` and `monetdb_data`).

### Reset / Delete All Persisted Data
```bash
# CAUTION: This permanently deletes all database records and volumes
docker compose down -v
```

## MonetDB First-Time Database Setup

When the MonetDB container boots up for the first time with an empty farm volume, a default database named `demo` is created. To create a dedicated `cinegraph` database:

```bash
# Create database
docker exec -it cinegraph-monetdb monetdb create cinegraph

# Start database
docker exec -it cinegraph-monetdb monetdb start cinegraph

# Release database for external client connections
docker exec -it cinegraph-monetdb monetdb release cinegraph
```
