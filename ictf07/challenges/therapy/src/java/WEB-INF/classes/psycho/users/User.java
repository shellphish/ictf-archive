package psycho.users;

public class User {
	
	private long id;
	private String username;
	private String password;
	private Roles role;
	private boolean hasComplain;
	
	public enum Roles {
		client,
		counselor
	};
	
	public enum Role {USER, CONSULTANT, ADMIN};
	
	public User() {
		id = 0;
		username = null;
		password = null;
		role = null;
		hasComplain = false;
	}
	
	public User(long user_id, String name, String pass, Roles userRole) {
		id = user_id;
		username = name;
		password = pass;
		role = userRole;
		hasComplain = false;
	}
	
	public long getUserId() {
		return id;
	}
	
	public void setHasComplain(boolean val) {
		hasComplain = val;
	}
	
	public boolean hasComplain() {
		return hasComplain;
	}
	
	public boolean isInRole(Roles r) {
		if(role.compareTo(r) == 0)
			return true;
		else 
			return false;
	}
	
	public static Roles getRole(String str) {
		if(Roles.client.toString().compareTo(str) == 0) 
			return Roles.client;
		else if(Roles.counselor.toString().compareTo(str) == 0)
			return Roles.counselor;
		else
			return null;
	}
	
	public static boolean isValidRole(String str) {
		Roles[] roles = Roles.values();
		for(int i = 0; i < roles.length; i++) {
			String role = roles[i].toString();
			if(role.compareTo(str) == 0)
				return true;
		}
		return false;
	}
	
	public void setUsername(String name) {
		username = name;
	}
	
	public void setPassword(String pass) {
		password = pass;
	}
	
	
	public String getUsername() {
		return username;
	}
	
	public String getPassword() {
		return password;
	}

	
	public boolean isValid() {
		if(username != null)
			return true;
		else
			return false;
	}
}
