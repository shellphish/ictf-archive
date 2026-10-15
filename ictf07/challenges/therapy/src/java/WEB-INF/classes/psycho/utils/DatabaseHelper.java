package psycho.utils;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Random;

import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.NamingException;
import javax.sql.DataSource;

import psycho.ApplicationResources;
import psycho.users.User;

public class DatabaseHelper {
	
	private static String userQuery = "select role, id from users where username=? and password=?";
	private static String complainQuery = "select * from complains where client_id = ?";
	private static String insertComplainQuery = "insert into complains(client_id, description, private_info) values (?,?,?)";
	
	private static String getCounselorsQuery = "select username from users where role = ?";
	private static String assignCounselorQuery = "update users set counselor = ? where username=? and password=?";
	private static String getUsersCounselorQuery = "select counselor from users where username=? and password=?";
	
	public static Connection getConnection() throws SQLException, NamingException {
		InitialContext initCtx = new InitialContext();
		Context envCtx = (Context)initCtx.lookup("java:/comp/env");
		DataSource ds = (DataSource)envCtx.lookup("jdbc/PsychoDB");
		Connection conn = ds.getConnection();
		
		return conn;
	}
	
	public static String createUser(String username, String password, String role, 
				String firstName, String lastName, String email) {
		String msg = null;
		
		try{ 
			Connection conn = DatabaseHelper.getConnection();
			PreparedStatement stmt1 = conn.prepareStatement("SELECT * from users where username=? and password=?");
			stmt1.setString(1, username);
			stmt1.setString(2, password);
			ResultSet results = stmt1.executeQuery();
			if(results.next()) {
				msg = "Illegal username or password";
				return msg;
			}
			
			PreparedStatement stmt = 
				conn.prepareStatement("INSERT into users(username, password, role, firstname, lastname, email) VALUES(?,?,?,?,?,?)");
			stmt.setString(1, username);
			stmt.setString(2, password);
			stmt.setString(3, role);
			stmt.setString(4, firstName);
			stmt.setString(5, lastName);
			stmt.setString(6, email);
			
			if(stmt.executeUpdate() == 0)
				msg = "a DB problem";
			conn.close();
		}
		catch(Exception e) {
			msg = e.getMessage();
		}
		return msg;
	}
	
	public static User getUser(String name, String pass) {
		User user = null;
		
		try {
			Connection conn = DatabaseHelper.getConnection();
			PreparedStatement stmt = conn.prepareStatement(userQuery);
			stmt.setString(1, name);
			stmt.setString(2, pass);
			ResultSet results = stmt.executeQuery();
			if(results.next()) {
				String role = results.getString(ApplicationResources.getRoleAttr());
				User.Roles validRole = User.getRole(role);
				long id = results.getLong("id");
				if(validRole != null)
					user = new User(id, name, pass, validRole);
			}
			conn.close();
		} catch (Exception e) {
			System.out.println("Database error: " + e.getMessage());
		}
		
		return user;
	}
	
	public static boolean hasComplain(long id) {
		boolean hasC = false;
		
		try {
			Connection conn = DatabaseHelper.getConnection();
			PreparedStatement stmt = conn.prepareStatement(complainQuery);
			stmt.setLong(1, id);
			ResultSet results = stmt.executeQuery();
			
			if(results.next()) {
				hasC = true;
			}
			conn.close();
		} catch (Exception e) {
			System.out.println("Database error: " + e.getMessage());
		}
		return hasC;
	}
	
	public static void assignCounselor(String username, String passwd) {
		
		if(username == null)
			return;
		
		try {
			Connection conn = DatabaseHelper.getConnection();
			PreparedStatement stmt = conn.prepareStatement(getCounselorsQuery);
			stmt.setString(1, User.Roles.counselor.toString());
			ResultSet results = stmt.executeQuery();
			
			if(results.last()) {
				int size = results.getRow();
				
				Random randGen = new Random(); 
				int id = randGen.nextInt(size) + 1;
				System.out.println("counselor id = " + id);
				results.absolute(id);
				String counselorName = results.getString("username");
				
				PreparedStatement stmt2 = conn.prepareStatement(assignCounselorQuery);
				stmt2.setString(1, counselorName);
				stmt2.setString(2, username);
				stmt2.setString(3, username);
				stmt2.executeUpdate();
			}
			conn.close();
		} catch (Exception e) {
			System.out.println("Database error: " + e.getMessage());
		}
		
	}
	
	public static String getCounselor(User user) {
		String counselor = null;
		
		if(user != null) {
			String username = user.getUsername();
			String passwd = user.getPassword();
			try {
				Connection conn = DatabaseHelper.getConnection();
				PreparedStatement stmt = conn.prepareStatement(getUsersCounselorQuery);
				stmt.setString(1, username);
				stmt.setString(2, passwd);
				ResultSet results = stmt.executeQuery();
				if(results.next()) {
					counselor = results.getString(1);
				}
			} catch (Exception e) {
				System.out.println("Database error: " + e.getMessage());
			}
		} 
		
		return counselor;
	}
	
	public static String createComplain(long id, String desc, String info) {
		String msg = null;
		
		System.out.println("inserting complain");
		if(desc == null || info == null) 
			msg = "NULL input";
		else {
			try{ 
				Connection conn = DatabaseHelper.getConnection();
				PreparedStatement stmt = 
					conn.prepareStatement(insertComplainQuery);
				stmt.setLong(1, id);
				stmt.setString(2, desc);
				stmt.setString(3, info);
				
				if(stmt.executeUpdate() == 0)
					msg = "a DB problem";
				conn.close();
			}
			catch(Exception e) {
				msg = e.getMessage();
			}
		}
		
		return msg;
	}
	
	public static String updateComplain(long id, String desc, String info) {
		String msg = null;
		
		System.out.println("updating complain");
		if(desc == null || info == null) 
			msg = "NULL input";
		else {
			try{ 
				String query = "UPDATE complains SET description='" + desc 
					+ "', private_info='" + info + "' where client_id=" + String.valueOf(id);
				
				Connection conn = DatabaseHelper.getConnection();
				Statement stmt = conn.createStatement();
				stmt.execute(query);
			
				if(stmt.getUpdateCount() < 0)
					msg = "a DB problem";
				conn.close();
			}
			catch(Exception e) {
				msg = e.getMessage();
			}
		}
		
		return msg;
	}
}
