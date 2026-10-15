package db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/** Opens the Swing application's MySQL connection from private runtime settings. */
public class DBConnection {

    private static DBConnection dbConnection;
    private Connection connection;

    private DBConnection() throws ClassNotFoundException, SQLException {
        connection = openConnection();
    }

    public static synchronized DBConnection getInstance() throws ClassNotFoundException, SQLException {
        if (dbConnection == null) {
            dbConnection = new DBConnection();
        }
        return dbConnection;
    }

    private static Connection openConnection() throws ClassNotFoundException, SQLException {
        String url = setting(
                "HOSTEL_DB_URL",
                "hostel.db.url",
                "jdbc:mysql://localhost:3306/nugasewana?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC"
        );
        String username = setting("HOSTEL_DB_USER", "hostel.db.user", "hostel_app");
        String password = setting("HOSTEL_DB_PASSWORD", "hostel.db.password", "");

        if (password.trim().isEmpty()) {
            throw new SQLException(
                    "MySQL password is not configured. Set HOSTEL_DB_PASSWORD before starting the application."
            );
        }

        Class.forName("com.mysql.cj.jdbc.Driver");
        return DriverManager.getConnection(url, username, password);
    }

    private static String setting(String environmentName, String propertyName, String defaultValue) {
        String value = System.getProperty(propertyName);
        if (value == null || value.trim().isEmpty()) {
            value = System.getenv(environmentName);
        }
        return value == null || value.trim().isEmpty() ? defaultValue : value.trim();
    }

    public synchronized Connection getConnection() throws ClassNotFoundException, SQLException {
        if (connection == null || connection.isClosed()) {
            connection = openConnection();
        }
        return connection;
    }
}
