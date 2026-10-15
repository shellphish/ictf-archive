package psycho;

import java.io.IOException;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import psycho.utils.Command;

public class ActionController extends HttpServlet {
	
	
	protected void processRequest(HttpServletRequest request, HttpServletResponse response) 
	throws ServletException, IOException {
		String page = null;
		try {
			RequestHelper helper = new RequestHelper(request);
			Command cmdHelper = helper.getCommand();
			
			page = cmdHelper.execute(request, response);
		} catch (Exception e) {
			request.setAttribute(ApplicationResources.getMessageAttr(), "Exception occurred (" 
						+ e.getClass() + "): "
						+ e.getMessage());
			page = ApplicationResources.getErrorPage();
		}
		dispatch(request, response, page);
	}
	
	protected void doGet(HttpServletRequest request, HttpServletResponse response) 
	throws ServletException, IOException {
		
		processRequest(request, response);
	}
	
	protected void doPost(HttpServletRequest request, HttpServletResponse response) 
	throws ServletException, IOException {
		
		processRequest(request, response);
	}
	
	public static void dispatch(HttpServletRequest request, 
   			HttpServletResponse response, 
   			String dest) 
   	throws ServletException, IOException {
   		RequestDispatcher dispatcher = request.getRequestDispatcher(dest);
   		dispatcher.forward(request, response);
   	}
}
