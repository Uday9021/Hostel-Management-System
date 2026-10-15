# Hostel Management System

This repository contains the original Java Swing/MySQL desktop application and a browser-based hostel room dashboard used for the CCA 2 Docker and Kubernetes demonstration.

## Applications

### Browser dashboard (`hostel-web/`)

- Lists hostel rooms and live totals for beds, occupancy, and availability.
- Adds rooms, updates occupied-bed counts, and deletes rooms.
- Validates room names and bed counts in the Flask API.
- Stores records in SQLite. The Kubernetes Deployment mounts a persistent volume claim at `/data`, so records survive a pod replacement or Jenkins redeployment while the PVC remains.
- The dashboard has its own SQLite database; it does not currently share data with the Swing application's MySQL database.

### Java desktop application (`HostelManagementSystem/`)

- NetBeans Java Swing application with hostel, room, guest, reservation, facility, and payment screens.
- Uses MySQL through JDBC. The database URL, username, and password are read from runtime settings instead of being embedded in Java source.
- Includes MySQL Connector/J 8.4.0 in the NetBeans project libraries for current MySQL servers.
- The compatible MySQL schema is in `HostelManagementSystem/database/schema.sql`.

## Run the browser dashboard locally

From the repository root:

```bash
cd hostel-web
python -m venv .venv
```

Activate the environment (`.venv\Scripts\activate.bat` in Windows CMD, or `source .venv/bin/activate` in Linux), then run:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m flask --app app run --host 0.0.0.0 --port 5000
```

Open `http://localhost:5000`. The local database defaults to `hostel-web/instance/hostel.db`; set `HOSTEL_DATABASE` to choose another database file.

## Set up MySQL for the Java desktop app

1. Start a local MySQL server. From the repository root, import the schema using the MySQL command-line client:

   ```text
   mysql -u root -p < HostelManagementSystem/database/schema.sql
   ```

2. In MySQL, create a dedicated application account and the first desktop login. Replace both example passwords with private values; do not commit real passwords:

   ```sql
   CREATE USER 'hostel_app'@'localhost' IDENTIFIED BY 'REPLACE_WITH_A_PRIVATE_DB_PASSWORD';
   GRANT SELECT, INSERT, UPDATE, DELETE ON nugasewana.* TO 'hostel_app'@'localhost';
   INSERT INTO nugasewana.user_account (UserName, password)
       VALUES ('admin', 'REPLACE_WITH_A_PRIVATE_LOGIN_PASSWORD');
   ```

3. Set these variables in the environment from which NetBeans is launched:

   ```text
   HOSTEL_DB_URL=jdbc:mysql://localhost:3306/nugasewana?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC
   HOSTEL_DB_USER=hostel_app
   HOSTEL_DB_PASSWORD=your-private-db-password
   ```

   The app also accepts Java system properties `hostel.db.url`, `hostel.db.user`, and `hostel.db.password`. The defaults target a local MySQL database named `nugasewana`, a user named `hostel_app`, and no password; the app displays an actionable error if no password is configured.

4. Open the NetBeans project at `HostelManagementSystem/` and run it. Use the `admin` login created in step 2.

The old root password has been removed from the source. The legacy login table still stores the desktop login password as supplied by this academic application; use a private demo password and do not expose this setup as a production authentication system.

## CI/CD deployment on Amazon Linux and Minikube

1. Create a public Docker Hub repository named `hostel-cicd` under `uday9021`.
2. In Jenkins, save the Docker Hub username and access token as a username/password credential with ID `dockerhub-creds`.
3. Configure a Jenkins Pipeline job with **Pipeline script from SCM**, repository `https://github.com/Uday9021/Hostel-Management-System.git`, branch `*/master`, and script path `Jenkinsfile`.
4. On the Amazon Linux Jenkins host, ensure Jenkins can use Git, Docker, `kubectl`, and Minikube. The Jenkins user needs a working Minikube kubeconfig.
5. Run the Jenkins job. It checks out the source, runs the six Flask unit tests in the Docker test target, builds a runtime image tagged with the 12-character Git commit ID and `latest`, pushes both tags to Docker Hub, applies the PVC and Service, then deploys the new image and waits for the rollout.
6. For the redeploy demonstration, push a source edit and run the pipeline again. Confirm that the new tagged image is in Docker Hub and that Kubernetes reports the rollout complete.

The image repository must be public for Kubernetes to pull it without an image-pull secret. The database PVC is local to the Minikube cluster on EC2; deleting the PVC or EC2 instance deletes its stored room records.

## Open the browser dashboard from the laptop

On the EC2 host, run this in an SSH terminal and leave it open during the demo:

```bash
sudo -u jenkins -H kubectl port-forward --address 0.0.0.0 service/hostel-web 8081:80
```

Allow inbound TCP port `8081` from your IP in the EC2 security group, then open `http://YOUR_EC2_PUBLIC_IP:8081` in the laptop browser. Port forwarding stops when the command or SSH session ends.
