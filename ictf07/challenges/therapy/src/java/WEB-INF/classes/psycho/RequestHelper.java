package psycho;

import java.lang.reflect.Constructor;
import java.util.HashMap;

import javax.servlet.http.HttpServletRequest;

import psycho.users.ClientManager;
import psycho.users.CreateUser;
import psycho.users.AccountManager;
import psycho.utils.Command;

public class RequestHelper {

	private Command cmd;
	public enum Commands {
		createuser(ApplicationResources.getNewUserPage(), CreateUser.class),
		login(ApplicationResources.getLoginPage(), AccountManager.class),
		logout(ApplicationResources.getLogoutPage(), AccountManager.class),
		client(ApplicationResources.getClientPage(), ClientManager.class);
		
		private Class cls;
		private String action;
		Commands(String s, Class c) {
			cls = c;
			action = s;
		}
		
		public Class getCmdClass() {return cls;}
		public String getActionName() { return action; }
	};
	
	public RequestHelper(HttpServletRequest request) throws Exception {
		String uri = request.getRequestURI();
		String path = request.getContextPath();
		String action = uri.replaceFirst(path, "");
		
		if(Commands.createuser.getActionName().compareTo(action) == 0) {
			Class cmdClass = Commands.createuser.getCmdClass();
			cmd = (Command)cmdClass.getConstructor((Class[])null).newInstance();
		} else if(Commands.login.getActionName().compareTo(action) == 0) {
			Class cmdClass = Commands.login.getCmdClass();
			cmd = (Command)cmdClass.getConstructor((Class[])null).newInstance();
		} else if(Commands.logout.getActionName().compareTo(action) == 0) {
			Class cmdClass = Commands.logout.getCmdClass();
			cmd = (Command)cmdClass.getConstructor((Class[])null).newInstance();
		} else if(Commands.client.getActionName().compareTo(action) == 0) {
			Class cmdClass = Commands.client.getCmdClass();
			cmd = (Command)cmdClass.getConstructor((Class[])null).newInstance();
		} else {
			throw new Exception("Illegal action: " + action);
		}
		
	}
	
	public Command getCommand() {
		
		return cmd; 
	}
}
