package psycho.users;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import psycho.ApplicationResources;
import psycho.utils.Command;
import psycho.utils.DatabaseHelper;

public class ClientManager implements Command {

	public ClientManager() {
		// TODO Auto-generated constructor stub
	}
	
	public String execute(HttpServletRequest request, HttpServletResponse response) {
		String msg = null;	
		String method = request.getMethod();
		String page = null;
		
		HttpSession sess = request.getSession();
		User user = (User)sess.getAttribute(ApplicationResources.getUserAttr());
		
		if(user == null) 
			msg = "You need to login to access this page";
		else {
			// only can view or create complain here
			if("GET".compareTo(method) == 0) { 
				String action = request.getParameter("action");
				if(ApplicationResources.getShowRequest().compareTo(action) == 0) {
					page = ApplicationResources.getComplainPage() + "?"
						+ ApplicationResources.getUserAttr() + "=" + user.getUserId()
						+ "&" + ApplicationResources.getPrivateAttr() 
						+ "=" + ApplicationResources.getYesRequest();
		
				} else if(ApplicationResources.getCreateRequest().compareTo(action) == 0) {
					page = ApplicationResources.getComplainForm();
				} else if(ApplicationResources.getCounselorRequest().compareTo(action) == 0) {
					page = ApplicationResources.getViewCounselorPage();
				} else {
					if(user.hasComplain()) {
						page = ApplicationResources.getComplainPage() + "?"
							+ ApplicationResources.getUserAttr() + "=" + user.getUserId()
							+ "&" + ApplicationResources.getPrivateAttr() 
							+ "=" + ApplicationResources.getYesRequest();
				
					} else {
						page = ApplicationResources.getComplainForm();
					}
				}
			} else if("POST".compareTo(method) == 0) {
				String action = request.getParameter("submit");
				
				if(ApplicationResources.getCreateRequest().compareTo(action) == 0) {
					String desc = request.getParameter("story");
					String info = request.getParameter("addinfo");
					msg = DatabaseHelper.createComplain(user.getUserId(), desc, info);
					if(msg == null) {
						user.setHasComplain(AccountManager.hasComplain(user.getUserId()));
						DatabaseHelper.assignCounselor(user.getUsername(), user.getPassword());
						page = ApplicationResources.getMainPage();
					}
				} else if(ApplicationResources.getEditRequest().compareTo(action) == 0) {
					String desc = request.getParameter("story");
					String info = request.getParameter("addinfo");
					msg = DatabaseHelper.updateComplain(user.getUserId(), desc, info);
					page = ApplicationResources.getMainPage();
				} else {
					msg = "Illegal request";
				}
			}
		}
		
		if(msg != null) {
			request.setAttribute(ApplicationResources.getMessageAttr(), msg);
		} 
		if(page != null)
			return page;
		else
			return ApplicationResources.getErrorPage();
	}
	
}
