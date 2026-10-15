# Java Swing Hostel Management System

This is the original NetBeans desktop application. It uses the MySQL schema in `database/schema.sql` and expects a MySQL server to be running separately.

The NetBeans project uses the bundled MySQL Connector/J 8.4.0 driver.

## Database setup

1. Import `database/schema.sql` into MySQL.
2. Create a local application account and first login. Replace the example values with private passwords; do not commit them:

   ```sql
   CREATE USER 'hostel_app'@'localhost' IDENTIFIED BY 'REPLACE_WITH_A_PRIVATE_DB_PASSWORD';
   GRANT SELECT, INSERT, UPDATE, DELETE ON nugasewana.* TO 'hostel_app'@'localhost';
   INSERT INTO nugasewana.user_account (UserName, password)
       VALUES ('admin', 'REPLACE_WITH_A_PRIVATE_LOGIN_PASSWORD');
   ```

3. Set `HOSTEL_DB_URL`, `HOSTEL_DB_USER`, and `HOSTEL_DB_PASSWORD` in the environment used to launch NetBeans. The default URL is `jdbc:mysql://127.0.0.1:3306/nugasewana` with MySQL connection options; the default username is `hostel_app`. A password must be supplied.
4. Open this folder as a NetBeans project and run it. Sign in with the account created in step 2.

The connection settings can also be supplied as Java system properties: `hostel.db.url`, `hostel.db.user`, and `hostel.db.password`.
