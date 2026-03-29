// UserService.java
import java.sql.*;

public class UserService {
    public void getUser(String username) throws Exception {
        Connection conn = null;

        // ❌ SQL Injection
        String query = "SELECT * FROM users WHERE name = '" + username + "'";

        Statement stmt = conn.createStatement();
        stmt.executeQuery(query);
    }
}