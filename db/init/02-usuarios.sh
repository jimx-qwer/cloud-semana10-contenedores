#!/bin/sh
set -eu

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" <<'SQL'

\getenv u1 DEMO_USER1
\getenv p1 DEMO_PASSWORD1
\getenv n1 DEMO_NAME1

\getenv u2 DEMO_USER2
\getenv p2 DEMO_PASSWORD2
\getenv n2 DEMO_NAME2

INSERT INTO usuarios (usuario, password_hash, nombre)
VALUES
    (:'u1', crypt(:'p1', gen_salt('bf', 12)), :'n1'),
    (:'u2', crypt(:'p2', gen_salt('bf', 12)), :'n2')
ON CONFLICT (usuario) DO NOTHING;

SQL