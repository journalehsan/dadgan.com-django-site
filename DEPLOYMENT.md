**Deployment & Migration Notes**

- **Migrate sqlite -> MySQL**: Use `./migrate_sqlite_to_mysql.sh` to convert the local `db.sqlite3` to a MySQL-compatible SQL file, upload it, and import into the remote MariaDB Docker container. The script performs best-effort SQL transforms; review the generated SQL in `./tmp_sql_migrate` before proceeding.

- **Deploy new app container**: Use `./sync_and_deploy.sh` to replace the remote container named `dadgan_app` while preserving the external port `4436` mapping. The script supports either pulling an image on the remote host (`--image`) or uploading a local image tar (`--load-image`).

- **Backups**: The deploy script creates backups in `/tmp/deploy_$$` on the remote host (exported FS and saved image tar). The migration script dumps the remote DB (if exists) to `/tmp/${REMOTE_DB_NAME}_before_import.sql` before importing.

- **Credentials**: Both scripts use `sshpass` for non-interactive SSH/SCP. Credentials are configured at the top of each script. For improved security, prefer SSH keys and remove `sshpass` usage.

- **Testing**: After deploy, test the site at `https://dadgan.com` (the server's nginx maps external port 4436 to the container). If TLS/Proxy is used, confirm the upstream container is serving on port `80`.

- **Caveats**:
  - The sqlite -> MySQL conversion is not guaranteed for complex schemas (custom types/triggers/constraints). Manual review may be required.
  - If the new app relies on environment variables, volumes, or other runtime flags, edit the `docker run` line in `sync_and_deploy.sh` to include them.

If you want, I can:
- update `sync_and_deploy.sh` to include environment/volume mappings used by the current container, or
- run a dry-run of the migration locally to show the converted SQL.
