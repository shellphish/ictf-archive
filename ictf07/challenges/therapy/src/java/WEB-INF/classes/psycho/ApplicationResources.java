package psycho;

public class ApplicationResources {

	private static final String mainPage = "/";
	
	private static final String errorPage = "/error";
	private static final String loginPage = "/login.do";
	private static final String loginForm = "/loginform";
	private static final String logoutPage = "/logout.do";
	
	private static final String newuserPage = "/createuser.do";
	private static final String newuserForm = "/userform";
	
	private static final String clientPage = "/clients.do";
	private static final String counselorPage = "/counselors.do";
	private static final String newComplainForm = "/complainform";
	private static final String complainPage = "/complain";
	private static final String viewCounselorPage = "/counselor";
	private static final String clientsInfoPage = "/clients";
	
	private static final String accountForm = "/account";
	private static final String accountPage = "/account.do";
	
	private static final String createRequest = "create";
	private static final String editRequest = "edit";
	private static final String showRequest = "show";
	private static final String counselorRequest = "counselor";
	private static final String clientRequest = "client";
	private static final String yesRequest = "true";
	private static final String noRequest = "false";
	
	private static final String msgAttr = "msg";
	private static final String userAttr = "user";
	private static final String roleAttr = "role";
	private static final String privateAttr = "show_private";

	
	public static String getMainPage() { return mainPage; }
	public static String getErrorPage() { return errorPage; }
	
	public static String getLoginPage() { return loginPage; }
	public static String getLoginForm() { return loginForm; }
	public static String getLogoutPage() { return logoutPage; }
	
	public static String getNewUserPage() { return newuserPage; }
	public static String getNewUserForm() { return newuserForm; }
	
	public static String getClientPage() { return clientPage; }
	public static String getCounselorPage() { return counselorPage; }
	
	public static String getCreateRequest() { return createRequest; }
	public static String getShowRequest() { return showRequest; }
	public static String getEditRequest() { return editRequest; }
	public static String getCounselorRequest() { return counselorRequest; }
	public static String getClientRequest() { return clientRequest; }
	public static String getViewCounselorPage() { return viewCounselorPage; }
	public static String getClientsInfoPage() { return clientsInfoPage; }
	
	public static String getAccountPage() { return accountPage; }
	public static String getAccountForm() { return accountForm; }
	
	public static String getComplainForm() { return newComplainForm; }
	public static String getComplainPage() { return complainPage; }
	
	public static String getMessageAttr() { return msgAttr; }
	public static String getUserAttr() { return userAttr; }
	public static String getRoleAttr() { return roleAttr; }
	public static String getPrivateAttr() { return privateAttr; }
	
	public static String getYesRequest() { return yesRequest; }
	public static String getNoRequest() { return noRequest; }
}
