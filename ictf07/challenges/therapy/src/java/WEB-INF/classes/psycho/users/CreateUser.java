package psycho.users;


import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import psycho.ApplicationResources;
import psycho.utils.Command;
import psycho.utils.DatabaseHelper;


/**
 * Servlet implementation class for Servlet: CreateUser
 *
 */
 public class CreateUser implements Command {
	static final long serialVersionUID = 1L;
   	
	public CreateUser() {
	}   	
	
	

	public String execute(HttpServletRequest request, HttpServletResponse response) {
		String msg = null;	
		String method = request.getMethod();
		String page = null;
		
		if("GET".compareTo(method) == 0) {
			String userType = (String)request.getParameter(ApplicationResources.getRoleAttr());
			if(userType == null || !(User.isValidRole(userType))) {
				msg = "You need to provide a valid user <b>role</b> parameter";
			} else {
				request.setAttribute(ApplicationResources.getRoleAttr(), userType);
				page = ApplicationResources.getNewUserForm();
			}
			
		} else if("POST".compareTo(method) == 0) {
			if(request.getParameter("submit") == null) {
				msg = this.getClass().getName() + ": Invalid request";
			} else {
				
				String username = request.getParameter("username");
				String password = request.getParameter("password");
				String firstName = request.getParameter("firstname");
				String lastName = request.getParameter("lastname");
				String email = request.getParameter("email");
				String role = request.getParameter("role");
				
				if(username == null || password == null || email == null || role == null
						|| firstName == null || lastName == null
						|| "".equals(username) || "".equals(password) || "".equals(email)
						|| !(User.isValidRole(role))) {
					msg = "One of required parameters is missing: username, password, email, role";
				} else {
					
					if(!checkInput(firstName))
						msg = "First name can only contain alpha-numeric characters";
					else if(!checkInput(lastName))
						msg = "Last name can only contain alpha-numeric characters";
					else if(!(checkEmail(email))){
						msg = "Email contains illegal characters";
					} else {
						msg = DatabaseHelper.createUser(username, password, role, firstName, lastName, email);
						if(msg == null)
							page = ApplicationResources.getLoginPage();
					}
				}
			}
		} else {
			msg = "Unsupported request method: " + method;
		}
		
		if(msg != null) {
			request.setAttribute("msg", msg);
		} 
		if(page != null)
			return page;
		else
			return ApplicationResources.getErrorPage();
	}   	
	
	private boolean checkInput(String str) {
		boolean isLegal = false;
		
		if(str.matches("[a-zA-Z0-9]*"))
			isLegal = true;
		
		return isLegal;
	}
	
	private boolean checkEmail(String str) {
		boolean isLegal = false;
		
		if(str.matches("[a-zA-Z0-9.-_@]*"))
			isLegal = true;
		
		return isLegal;
	}
}