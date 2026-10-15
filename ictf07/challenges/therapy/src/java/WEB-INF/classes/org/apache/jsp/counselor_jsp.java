package org.apache.jsp;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.jsp.*;
import psycho.ApplicationResources;
import psycho.users.User;
import psycho.utils.DatabaseHelper;
import psycho.ApplicationResources;
import psycho.users.AccountManager;

public final class counselor_jsp extends org.apache.jasper.runtime.HttpJspBase
    implements org.apache.jasper.runtime.JspSourceDependent {

  private static final JspFactory _jspxFactory = JspFactory.getDefaultFactory();

  private static java.util.List _jspx_dependants;

  static {
    _jspx_dependants = new java.util.ArrayList(3);
    _jspx_dependants.add("/static/header.html");
    _jspx_dependants.add("/menu.jsp");
    _jspx_dependants.add("/static/footer.html");
  }

  private org.apache.jasper.runtime.TagHandlerPool _005fjspx_005ftagPool_005fsql_005fquery_005fvar_005fdataSource;
  private org.apache.jasper.runtime.TagHandlerPool _005fjspx_005ftagPool_005fsql_005fparam_005fvalue_005fnobody;
  private org.apache.jasper.runtime.TagHandlerPool _005fjspx_005ftagPool_005fc_005fforEach_005fvar_005fitems;

  private javax.el.ExpressionFactory _el_expressionfactory;
  private org.apache.AnnotationProcessor _jsp_annotationprocessor;

  public Object getDependants() {
    return _jspx_dependants;
  }

  public void _jspInit() {
    _005fjspx_005ftagPool_005fsql_005fquery_005fvar_005fdataSource = org.apache.jasper.runtime.TagHandlerPool.getTagHandlerPool(getServletConfig());
    _005fjspx_005ftagPool_005fsql_005fparam_005fvalue_005fnobody = org.apache.jasper.runtime.TagHandlerPool.getTagHandlerPool(getServletConfig());
    _005fjspx_005ftagPool_005fc_005fforEach_005fvar_005fitems = org.apache.jasper.runtime.TagHandlerPool.getTagHandlerPool(getServletConfig());
    _el_expressionfactory = _jspxFactory.getJspApplicationContext(getServletConfig().getServletContext()).getExpressionFactory();
    _jsp_annotationprocessor = (org.apache.AnnotationProcessor) getServletConfig().getServletContext().getAttribute(org.apache.AnnotationProcessor.class.getName());
  }

  public void _jspDestroy() {
    _005fjspx_005ftagPool_005fsql_005fquery_005fvar_005fdataSource.release();
    _005fjspx_005ftagPool_005fsql_005fparam_005fvalue_005fnobody.release();
    _005fjspx_005ftagPool_005fc_005fforEach_005fvar_005fitems.release();
  }

  public void _jspService(HttpServletRequest request, HttpServletResponse response)
        throws java.io.IOException, ServletException {

    PageContext pageContext = null;
    HttpSession session = null;
    ServletContext application = null;
    ServletConfig config = null;
    JspWriter out = null;
    Object page = this;
    JspWriter _jspx_out = null;
    PageContext _jspx_page_context = null;


    try {
      response.setContentType("text/html; charset=UTF-8");
      pageContext = _jspxFactory.getPageContext(this, request, response,
      			null, true, 8192, true);
      _jspx_page_context = pageContext;
      application = pageContext.getServletContext();
      config = pageContext.getServletConfig();
      session = pageContext.getSession();
      out = pageContext.getOut();
      _jspx_out = out;

      out.write("\n    \n\n\n\n \n \n \n \n ");
      out.write("\n<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\"><head>\n\n\n\n\n  <meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">\n    \n    <meta name=\"Generator\" content=\"iWeb 2.0.2\">\n    <meta name=\"iWeb-Build\" content=\"local-build-20071129\">\n    <meta name=\"viewport\" content=\"width=700\"><title>THE MAFIA Music and Film Industry Association</title>\n    \n    <link rel=\"stylesheet\" type=\"text/css\" media=\"screen,print\" href=\"/Therapy_files/Therapy.css\"><!--[if IE]><link rel='stylesheet' type='text/css' media='screen,print' href='/Therapy_files/TherapyIE.css'/><![endif]-->\n    <style type=\"text/css\">\n/*<![CDATA[*/\n\t@import \"Scripts/Widgets/HTMLRegion/Paste.css\";\n/*]]>*/\n</style>\n    <script type=\"text/javascript\" src=\"/Therapy_files/iWebSite.js\"></script>\n    <script type=\"text/javascript\" src=\"/Therapy_files/WidgetCommon.js\"></script>\n    <script type=\"text/javascript\" src=\"/Therapy_files/navbar.js\"></script>\n");
      out.write("    <script type=\"text/javascript\" src=\"/Therapy_files/Paste.js\"></script>\n    <script type=\"text/javascript\" src=\"/Therapy_files/Therapy.js\"></script><style type=\"text/css\">div#widget0 .navbar {\n\tfont-family: 'Courier New', Courier, monospace, serif;\n\tfont-size: 1.1em;\n\tcolor: #AFAA9F;\n\tmargin: -2px 0 0 0px;\n\tline-height: 20px;\n\tpadding: 5px 0 12px 0;\n\tfont-weight: bold;\n\tbackground-image: url(/Therapy_files/navfill-v2_1.jpg);\n}\n\ndiv#widget0 .navbar-bg {\n\ttext-align: left;\n}\n\ndiv#widget0 .navbar-bg ul {\n\tlist-style: none;\n\tmargin: 0px;\n\tpadding: 0 10px 0 30px;\n}\n\n\ndiv#widget0 li {\n\tlist-style-type: none;\n\tdisplay: inline;\n\tpadding: 0px 25px 0 0;\n}\n\n\ndiv#widget0 li a {\n\ttext-decoration: none;\n\tcolor: #AFAA9F;\n}\n\ndiv#widget0 li a:visited {\n\ttext-decoration: none;\n\tcolor: #AFAA9F;\n}\n\ndiv#widget0 li a:hover\n{\n \tcolor: #D64600;\n}\n\n\ndiv#widget0 li.current-page a\n{\n\t color: #fff;\n\n}\n</style><link href=\"/Therapy_files/TherapyMoz.css\" type=\"text/css\" rel=\"stylesheet\"></head><body style=\"margin: 0pt; background: rgb(19, 16, 16) none repeat scroll 0%%; -moz-background-clip: -moz-initial; -moz-background-origin: -moz-initial; -moz-background-inline-policy: -moz-initial;\" onload=\"onPageLoad();\" onunload=\"onPageUnload();\">\n");
      out.write("    <div style=\"text-align: center;\">\n      <div style=\"margin: 0px auto; overflow: hidden; position: relative; text-align: left; width: 700px;\" id=\"body_content\">\n        <div style=\"background: transparent url(/Therapy_files/rp_tile_v6.jpg) repeat scroll left top; -moz-background-clip: -moz-initial; -moz-background-origin: -moz-initial; -moz-background-inline-policy: -moz-initial; width: 700px;\">\n          <div style=\"height: 139px; margin-left: 0px; position: relative; width: 700px; z-index: 10;\" id=\"header_layer\">\n            <div style=\"height: 0px; line-height: 0px;\" class=\"bumper\">&nbsp;</div>\n            <div style=\"height: 139px; left: 32px; position: absolute; top: 0px; width: 635px; z-index: 1;\" class=\"tinyText\">\n              <div style=\"position: relative; width: 635px;\">\n                <img src=\"/Therapy_files/shapeimage_1.png\" alt=\"\" style=\"height: 107px; left: 0px; margin-left: 0px; margin-top: 24px; position: absolute; top: 0px; width: 471px;\">\n              </div>\n            </div>\n          </div>\n");
      out.write("          <div style=\"margin-left: 0px; position: relative; width: 700px; z-index: 0;\" id=\"nav_layer\">\n            <div style=\"height: 0px; line-height: 0px;\" class=\"bumper\">&nbsp;</div>\n            <div style=\"height: 490px; left: 0px; position: absolute; top: -489px; width: 700px; z-index: 1;\" class=\"tinyText style_SkipStroke\">\n              <img src=\"/Therapy_files/navfill-v2.jpg\" alt=\"\" style=\"border: medium none ; height: 490px; width: 700px;\">\n            </div>\n            <div style=\"height: 1px; line-height: 1px;\" class=\"tinyText\">&nbsp;</div>\n            <div class=\"com-apple-iweb-widget-navbar flowDefining\" id=\"widget0\" style=\"margin-left: 0px; margin-top: -1px; position: relative; width: 700px; z-index: 1;\">\n    \n              <div id=\"widget0-navbar\" class=\"navbar\">\n\n      \n                <div id=\"widget0-bg\" class=\"navbar-bg\">\n\n        \n                  <ul id=\"widget0-navbar-list\" class=\"navbar-list\"><li class=\"noncurrent-page\"><a href=\"/Site/Welcome.html\">Welcome </a></li><li class=\"noncurrent-page\"><a href=\"/Site/About_us.html\">About&nbsp;us </a></li><li class=\"noncurrent-page\"><a href=\"/Site/MAFIA_people.html\">MAFIA&nbsp;people </a></li><li class=\"noncurrent-page\"><a href=\"/Site/Petition.html\">Petition </a></li><li class=\"noncurrent-page\"><a href=\"/Site/Would_you.html\">Would&nbsp;you? </a></li><li class=\"noncurrent-page\"><a href=\"/Site/Sound_of_music.html\">Sound&nbsp;of&nbsp;music </a></li><li class=\"noncurrent-page\"><a href=\"/Site/Blog/Blog.html\">Blog </a></li><li class=\"noncurrent-page\"><a href=\"/Site/Bosses_and_artists.html\">Bosses&nbsp;and&nbsp;artists </a></li><li class=\"noncurrent-page\"><a href=\"/Site/Make_amends.html\">Make&nbsp;amends </a></li></ul>\n");
      out.write("                  \n      \n</div>\n                \n    \n</div>\n            </div>\n            <script type=\"text/javascript\"><!--//--><![CDATA[//><!--\nnew NavBar('widget0', 'Scripts/Widgets/Navbar', 'Scripts/Widgets/SharedResources', '.', {\"current-page-GUID\": \"84D1B46D-2189-4E49-A038-45F3E1D80F00\", \"path-to-root\": \"\", \"isCollectionPage\": \"NO\", \"navbar-css\": \".navbar {\\n\\tfont-family: 'Courier New', Courier, monospace, serif;\\n\\tfont-size: 1.1em;\\n\\tcolor: #AFAA9F;\\n\\tmargin: -2px 0 0 0px;\\n\\tline-height: 20px;\\n\\tpadding: 5px 0 12px 0;\\n\\tfont-weight: bold;\\n\\tbackground-image: url(/Therapy_files\\/navfill-v2_1.jpg);\\n}\\n\\n.navbar-bg {\\n\\ttext-align: left;\\n}\\n\\n.navbar-bg ul {\\n\\tlist-style: none;\\n\\tmargin: 0px;\\n\\tpadding: 0 10px 0 30px;\\n}\\n\\n\\nli {\\n\\tlist-style-type: none;\\n\\tdisplay: inline;\\n\\tpadding: 0px 25px 0 0;\\n}\\n\\n\\nli a {\\n\\ttext-decoration: none;\\n\\tcolor: #AFAA9F;\\n}\\n\\nli a:visited {\\n\\ttext-decoration: none;\\n\\tcolor: #AFAA9F;\\n}\\n\\nli a:hover\\n{\\n \\tcolor: #D64600;\\n}\\n\\n\\nli.current-page a\\n{\\n\\t color: #fff;\\n\\n}\\n\"});\n");
      out.write("//--><!]]></script>\n            <div style=\"clear: both; height: 0px; line-height: 0px;\" class=\"spacer\">&nbsp;</div>\n          </div>\n          <div style=\"margin-left: 0px; position: relative; width: 700px; z-index: 5;\" id=\"body_layer\">\n            <div style=\"height: 0px; line-height: 0px;\" class=\"bumper\">&nbsp;</div>\n            <div style=\"height: 25px; left: 0px; position: absolute; top: -15px; width: 700px; z-index: 1;\" class=\"tinyText style_SkipStroke_1\">\n              <img src=\"/Therapy_files/pagetop10.png\" alt=\"\" style=\"border: medium none ; height: 25px; width: 700px;\">\n            </div>\n            \n\n\n            <div id=\"id1\" style=\"height: 100px; left: 308px; position: absolute; top: 405px; width: 100px; z-index: 1;\" class=\"style_SkipStroke_2\">\n              <div class=\"text-content graphic_textbox_layout_style_default_External_100_100\" style=\"padding: 0px;\">\n                <div class=\"graphic_textbox_layout_style_default\"></div>\n              </div>\n            </div>\n            \n\n\n            <div id=\"id2\" style=\"height: 100px; left: 63px; position: absolute; top: 112px; width: 532px; z-index: 1;\" class=\"style_SkipStroke_2\">\n");
      out.write("              <div class=\"text-content graphic_textbox_layout_style_default_External_532_100\" style=\"padding: 0px;\">\n                <div class=\"graphic_textbox_layout_style_default\">\n                  ");
      out.write("\n\n<h1 class=\"Title\">The Best Counselor For You</h1>\n\t");
 HttpSession s = request.getSession();
	   User user = (User)s.getAttribute(ApplicationResources.getUserAttr());
	   String counselor = DatabaseHelper.getCounselor(user);
	   
	   if(counselor == null) {
	
      out.write("\n\t\t<p class=\"Body\">If you see this message, our system determined that there \n\t\t\tis no perfect counselor available for you yet. Please, stay in touch \n\t\t\tand you will be notified when your match is found.</p>\n\t");
 } else {
	
	
	
      out.write("\n\t\n\t");
      //  sql:query
      org.apache.taglibs.standard.tag.rt.sql.QueryTag _jspx_th_sql_005fquery_005f0 = (org.apache.taglibs.standard.tag.rt.sql.QueryTag) _005fjspx_005ftagPool_005fsql_005fquery_005fvar_005fdataSource.get(org.apache.taglibs.standard.tag.rt.sql.QueryTag.class);
      _jspx_th_sql_005fquery_005f0.setPageContext(_jspx_page_context);
      _jspx_th_sql_005fquery_005f0.setParent(null);
      // /counselor.jsp(28,1) name = var type = java.lang.String reqTime = false required = true fragment = false deferredValue = false expectedTypeName = null deferredMethod = false methodSignature = null
      _jspx_th_sql_005fquery_005f0.setVar("rs");
      // /counselor.jsp(28,1) name = dataSource type = null reqTime = true required = false fragment = false deferredValue = false expectedTypeName = null deferredMethod = false methodSignature = null
      _jspx_th_sql_005fquery_005f0.setDataSource(new String("jdbc/PsychoDB"));
      int[] _jspx_push_body_count_sql_005fquery_005f0 = new int[] { 0 };
      try {
        int _jspx_eval_sql_005fquery_005f0 = _jspx_th_sql_005fquery_005f0.doStartTag();
        if (_jspx_eval_sql_005fquery_005f0 != javax.servlet.jsp.tagext.Tag.SKIP_BODY) {
          if (_jspx_eval_sql_005fquery_005f0 != javax.servlet.jsp.tagext.Tag.EVAL_BODY_INCLUDE) {
            out = _jspx_page_context.pushBody();
            _jspx_push_body_count_sql_005fquery_005f0[0]++;
            _jspx_th_sql_005fquery_005f0.setBodyContent((javax.servlet.jsp.tagext.BodyContent) out);
            _jspx_th_sql_005fquery_005f0.doInitBody();
          }
          do {
            out.write("\n\t\tselect firstname, lastname, email from users where username=?\n\t\t");
            //  sql:param
            org.apache.taglibs.standard.tag.rt.sql.ParamTag _jspx_th_sql_005fparam_005f0 = (org.apache.taglibs.standard.tag.rt.sql.ParamTag) _005fjspx_005ftagPool_005fsql_005fparam_005fvalue_005fnobody.get(org.apache.taglibs.standard.tag.rt.sql.ParamTag.class);
            _jspx_th_sql_005fparam_005f0.setPageContext(_jspx_page_context);
            _jspx_th_sql_005fparam_005f0.setParent((javax.servlet.jsp.tagext.Tag) _jspx_th_sql_005fquery_005f0);
            // /counselor.jsp(30,2) name = value type = null reqTime = true required = false fragment = false deferredValue = false expectedTypeName = null deferredMethod = false methodSignature = null
            _jspx_th_sql_005fparam_005f0.setValue( counselor );
            int _jspx_eval_sql_005fparam_005f0 = _jspx_th_sql_005fparam_005f0.doStartTag();
            if (_jspx_th_sql_005fparam_005f0.doEndTag() == javax.servlet.jsp.tagext.Tag.SKIP_PAGE) {
              _005fjspx_005ftagPool_005fsql_005fparam_005fvalue_005fnobody.reuse(_jspx_th_sql_005fparam_005f0);
              return;
            }
            _005fjspx_005ftagPool_005fsql_005fparam_005fvalue_005fnobody.reuse(_jspx_th_sql_005fparam_005f0);
            out.write('\n');
            out.write('	');
            int evalDoAfterBody = _jspx_th_sql_005fquery_005f0.doAfterBody();
            if (evalDoAfterBody != javax.servlet.jsp.tagext.BodyTag.EVAL_BODY_AGAIN)
              break;
          } while (true);
          if (_jspx_eval_sql_005fquery_005f0 != javax.servlet.jsp.tagext.Tag.EVAL_BODY_INCLUDE) {
            out = _jspx_page_context.popBody();
            _jspx_push_body_count_sql_005fquery_005f0[0]--;
          }
        }
        if (_jspx_th_sql_005fquery_005f0.doEndTag() == javax.servlet.jsp.tagext.Tag.SKIP_PAGE) {
          return;
        }
      } catch (Throwable _jspx_exception) {
        while (_jspx_push_body_count_sql_005fquery_005f0[0]-- > 0)
          out = _jspx_page_context.popBody();
        _jspx_th_sql_005fquery_005f0.doCatch(_jspx_exception);
      } finally {
        _jspx_th_sql_005fquery_005f0.doFinally();
        _005fjspx_005ftagPool_005fsql_005fquery_005fvar_005fdataSource.reuse(_jspx_th_sql_005fquery_005f0);
      }
      out.write("\n\n\t<table>\n\t\t");
      if (_jspx_meth_c_005fforEach_005f0(_jspx_page_context))
        return;
      out.write("\n\t</table>\n\t");
 } 
      out.write("\n\t<br/>\n\t<p class=\"Body\">Note: MAFIA is not responsible for the correctness of the counselor's information</p>\n ");
      out.write(" <!-- <div style=\"clear: both; height: 0px; line-height: 0px; \" class=\"spacer\"> </div> -->\n\n\n\n<div id=\"footer\"> \n<hr/>\n");

	HttpSession sess = request.getSession();
	String path = request.getContextPath();
	out.println("<a class=\"button\" href=\"" + path + "/\">Therapy Home</a>");
  	if(AccountManager.isUserAuthenticated(sess)) {
  		out.println("<a class=\"button\" href=\"" 
  		+ path + ApplicationResources.getLogoutPage() 
  		+ "\">Logout</a>");
  	} else {
  		out.println("<a class=\"button\" href=\"" + path + ApplicationResources.getLoginPage() + "\">Login</a>");
  		out.println("<a class=\"button\" href=\"" + path + ApplicationResources.getNewUserPage() + "?role=client" + "\">Sign Up</a>");
  		out.println("<a class=\"button\" href=\"" + path + ApplicationResources.getNewUserPage() + "?role=counselor" + "\">Become Counselor</a>");
  	}

      out.write("\n</div> \n");
      out.write('\n');
      out.write(' ');
      out.write("                </div>\n              </div>\n            </div>\n            <script type=\"text/javascript\"><!--//--><![CDATA[//><!--\nnew Paste('widget1', 'Scripts/Widgets/HTMLRegion', 'Scripts/Widgets/SharedResources', '.', {});\n//--><!]]></script>\n            <div style=\"height: 505px; line-height: 505px;\" class=\"spacer\">&nbsp;</div>\n          </div>\n          <div style=\"height: 100px; margin-left: 0px; position: relative; width: 700px; z-index: 15;\" id=\"footer_layer\">\n            <div style=\"height: 0px; line-height: 0px;\" class=\"bumper\">&nbsp;</div>\n          </div>\n        </div>\n      </div>\n    </div>\n  </body></html>");
    } catch (Throwable t) {
      if (!(t instanceof SkipPageException)){
        out = _jspx_out;
        if (out != null && out.getBufferSize() != 0)
          try { out.clearBuffer(); } catch (java.io.IOException e) {}
        if (_jspx_page_context != null) _jspx_page_context.handlePageException(t);
      }
    } finally {
      _jspxFactory.releasePageContext(_jspx_page_context);
    }
  }

  private boolean _jspx_meth_c_005fforEach_005f0(PageContext _jspx_page_context)
          throws Throwable {
    PageContext pageContext = _jspx_page_context;
    JspWriter out = _jspx_page_context.getOut();
    //  c:forEach
    org.apache.taglibs.standard.tag.rt.core.ForEachTag _jspx_th_c_005fforEach_005f0 = (org.apache.taglibs.standard.tag.rt.core.ForEachTag) _005fjspx_005ftagPool_005fc_005fforEach_005fvar_005fitems.get(org.apache.taglibs.standard.tag.rt.core.ForEachTag.class);
    _jspx_th_c_005fforEach_005f0.setPageContext(_jspx_page_context);
    _jspx_th_c_005fforEach_005f0.setParent(null);
    // /counselor.jsp(34,2) name = var type = java.lang.String reqTime = false required = false fragment = false deferredValue = false expectedTypeName = null deferredMethod = false methodSignature = null
    _jspx_th_c_005fforEach_005f0.setVar("row");
    // /counselor.jsp(34,2) name = items type = java.lang.Object reqTime = true required = false fragment = false deferredValue = false expectedTypeName = null deferredMethod = false methodSignature = null
    _jspx_th_c_005fforEach_005f0.setItems((java.lang.Object) org.apache.jasper.runtime.PageContextImpl.proprietaryEvaluate("${rs.rows}", java.lang.Object.class, (PageContext)_jspx_page_context, null, false));
    int[] _jspx_push_body_count_c_005fforEach_005f0 = new int[] { 0 };
    try {
      int _jspx_eval_c_005fforEach_005f0 = _jspx_th_c_005fforEach_005f0.doStartTag();
      if (_jspx_eval_c_005fforEach_005f0 != javax.servlet.jsp.tagext.Tag.SKIP_BODY) {
        do {
          out.write("\n\t\t<tr><td>First Name:  </td><td>");
          out.write((java.lang.String) org.apache.jasper.runtime.PageContextImpl.proprietaryEvaluate("${row.firstname}", java.lang.String.class, (PageContext)_jspx_page_context, null, false));
          out.write("</td></tr>\n\t\t<tr><td>Last Name:</td><td>");
          out.write((java.lang.String) org.apache.jasper.runtime.PageContextImpl.proprietaryEvaluate("${row.lastname}", java.lang.String.class, (PageContext)_jspx_page_context, null, false));
          out.write("</td></tr>\n\t\t<tr><td>Email:</td><td>");
          out.write((java.lang.String) org.apache.jasper.runtime.PageContextImpl.proprietaryEvaluate("${row.email}", java.lang.String.class, (PageContext)_jspx_page_context, null, false));
          out.write("</td></tr>\n\t\t");
          int evalDoAfterBody = _jspx_th_c_005fforEach_005f0.doAfterBody();
          if (evalDoAfterBody != javax.servlet.jsp.tagext.BodyTag.EVAL_BODY_AGAIN)
            break;
        } while (true);
      }
      if (_jspx_th_c_005fforEach_005f0.doEndTag() == javax.servlet.jsp.tagext.Tag.SKIP_PAGE) {
        return true;
      }
    } catch (Throwable _jspx_exception) {
      while (_jspx_push_body_count_c_005fforEach_005f0[0]-- > 0)
        out = _jspx_page_context.popBody();
      _jspx_th_c_005fforEach_005f0.doCatch(_jspx_exception);
    } finally {
      _jspx_th_c_005fforEach_005f0.doFinally();
      _005fjspx_005ftagPool_005fc_005fforEach_005fvar_005fitems.reuse(_jspx_th_c_005fforEach_005f0);
    }
    return false;
  }
}
