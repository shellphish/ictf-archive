package psycho.users;


import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import psycho.ApplicationResources;
import psycho.users.User;
import psycho.utils.Command;
import psycho.utils.DatabaseHelper;

public class AccountManager implements Command {

	
	
	
	public AccountManager() {
	}   	
	
	public String execute(HttpServletRequest request, HttpServletResponse response) {
	
		String msg = null;	
		String method = request.getMethod();
		String page = null;
		
		if("GET".compareTo(method) == 0) {
			String uri = request.getRequestURI();
			String path = request.getContextPath();
			String action = uri.replaceFirst(path, "");
			if(action.compareTo(ApplicationResources.getLogoutPage()) == 0) {
				HttpSession session = request.getSession();
				session.invalidate();
				page = ApplicationResources.getMainPage();
			} else if(action.compareTo(ApplicationResources.getLoginPage()) == 0){
				page = ApplicationResources.getLoginForm();
			} else {
				msg = "Invalid request";
			}
		} else if("POST".compareTo(method) == 0) {
			
			if(request.getParameter("login") == null) {
				page = ApplicationResources.getLoginForm();
			}
			String username = request.getParameter("username");
			String password = request.getParameter("password");
			
			User user = DatabaseHelper.getUser(username, password);
			
			if(user != null && user.isValid()) {
				user.setHasComplain(hasComplain(user.getUserId()));
				HttpSession sess = request.getSession();
				sess.setAttribute(ApplicationResources.getUserAttr(), user);
				page = ApplicationResources.getMainPage();
			} else {
				msg = "Login Failed";
			}
			
		} else {
			msg = "Unsupported request method: " + method;
		}
		
		if(msg != null) {
			request.setAttribute(ApplicationResources.getMessageAttr(), msg);
		} 
		if(page != null)
			return page;
		else
			return ApplicationResources.getErrorPage();
		
	}
	
	

	
	
	public static boolean hasComplain(long id) {
		return DatabaseHelper.hasComplain(id);

	}
	
	public static boolean isAuthenticated(User user) {
		if(user != null && user.isValid())
			return true;
		else
			return false;
	}
	
	public static boolean isUserAuthenticated(HttpSession sess) {
		User user = (User)sess.getAttribute(ApplicationResources.getUserAttr());
		return isAuthenticated(user);
	}
	
}
