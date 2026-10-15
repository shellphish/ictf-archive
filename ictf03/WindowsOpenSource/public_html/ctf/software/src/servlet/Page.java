/**
 * Page superclass.
 */

package ctf;

import java.io.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;

/**
 * Page superclass.
 */
public class Page
{
  /** Request */
  private HttpServletRequest req;

  /** Reponse */
  private HttpServletResponse resp;

  /** Title */
  private String title;

  /** Body */
  private String body;

  /**
   * Create a new page.
   *
   * @param req Request.
   * @param resp Response.
   * @param body Body.
   */
  public Page(HttpServletRequest req, HttpServletResponse resp,
    String title, String body)
  {
    this.req = req;
    this.resp = resp;
    this.title = title;
    this.body = body;
  }

  /**
   * Return section select.
   */
/*
  public static String getSectionSelect()
  {
    return
"<select name=\"section\">\n" +
"<option value=\"Racketeering\">Racketeering</option>\n" +
"<option value=\"Prostitution\">Prostitution</option>\n" +
"<option value=\"Gambling\">Gambling</option>\n" +
"<option value=\"Narcotics\">Narcotics</option>\n" +
"<option value=\"Animal Kumate\">Animal Kumate</option>\n" +
"</select>\n";
  }
*/

  /**
   * Output page.
   *
   * @throws IOException If unable to output page.
   */
  public void output()
    throws IOException
  {
    PrintWriter w = resp.getWriter();
    resp.setContentType("text/html");

    HttpSession s = req.getSession(false);
    String status;

    w.println(
"<html>" +
"<head>" +
"  <meta content=" +
"  \"HTML Tidy for Linux/x86 (vers 1st April 2003), see www.w3.org\"" +
"  name=\"generator\">" +
"  <meta http-equiv=\"Content-Type\" content=" +
"  \"text/html; charset=us-ascii\">" +
"  <meta name=\"ms.locale\" content=\"en-us\">" +
"  <meta name=\"Description\" content=" +
"  \"Enter a query to find downloads, support information, and other content on the Microsoft Web site.\">" +
"" +
"  <title>Search Microsoft.com</title>" +
"  <link rel=\"stylesheet\" type=\"text/css\" href=\"up.css\">" +
"  <link type=\"text/css\" rel=\"Stylesheet\" href=\"css.css\">" +
"</head>" +
"" +
"<body>" +
"  <a name=\"top\"></a><a href=\"#mainContent\" style=" +
"  \"display: none;\">Click here to jump to main page content</a>" +
"  <table id=\"mnpMastheadTable\" width=\"100%\" cellpadding=\"0\"" +
"  cellspacing=\"0\" border=\"0\" bgcolor=\"#0A6CCE\" dir=\"ltr\">" +
"    <tbody>" +
"      <tr>" +
"        <td width=\"100%\" valign=\"top\" rowspan=\"2\"><a href=" +
"        \"../index.html\"><img border=\"0\" src=" +
"        \"bnr_microsoft.gif\" alt=\"Microsoft Home\"></a></td>" +
"" +
"        <td valign=\"top\" height=\"20\" width=\"19\" align=\"right\">" +
"        <img alt=\"*\" src=\"curveLTR.gif\"></td>" +
"" +
"        <td valign=\"middle\" nowrap=\"nowrap\" colspan=\"2\" class=" +
"        \"mnpGlobalToolbar\" hover=\"#FFCC00\">&nbsp;&nbsp;<a class=" +
"        \"mnpGlobalToolbarLink\" dir=\"ltr\" href=" +
"        \"../products/index.html\"" +
"           target=\"_parent\" guid=" +
"           \"m71a06c18019585dbc34a9c4c641a3a08\">Products</a>&nbsp;&nbsp;|&nbsp;&nbsp;<a class=\"mnpGlobalToolbarLink\"" +
"           dir=\"ltr\" href=" +
"           \"../downloads/index.html\"" +
"           target=\"_parent\" guid=" +
"           \"medf9a186fb918ffce063d27c6d67cffe\">Downloads</a>&nbsp;&nbsp;|&nbsp;&nbsp;<a class=\"mnpGlobalToolbarLink\"" +
"           dir=\"ltr\" href=\"../support/index.html\" target=" +
"           \"_parent\" guid=" +
"           \"m1b3560fa9d8189ce386c2508f94c616f\">Support</a>&nbsp;&nbsp;|&nbsp;&nbsp;<a class=\"mnpGlobalToolbarLink\"" +
"           dir=\"ltr\" href=" +
"           \"search\"" +
"           target=\"_parent\" guid=" +
"           \"mc56a833edd4edfae7787c623c8510629\">Search</a>&nbsp;&nbsp;|&nbsp;&nbsp;<a class=\"mnpGlobalToolbarLink\"" +
"           dir=\"ltr\" href=" +
"           \"admin\"" +
"           target=\"_parent\" guid=" +
"           \"mc56a833edd4edfae7787c623c8510629\">Admin</a>&nbsp;&nbsp;|&nbsp;&nbsp;<a class=\"mnpGlobalToolbarLink\"" +
"           dir=\"ltr\" href=" +
"           \"../index.html\"" +
"           target=\"_parent\" guid=" +
"           \"m7367a73751f32aeeeff7c8b6363bded0\">Microsoft</a>&nbsp;&nbsp;</td>" +
"      </tr>" +
"" +
"      <tr>" +
"        <td width=\"19\">&nbsp;</td>" +
"" +
"        <td valign=\"top\" height=\"40\" nowrap=\"nowrap\">&nbsp;</td>" +
"" +
"        <td valign=\"top\" height=\"40\" nowrap=\"nowrap\" class=" +
"        \"mnpMastheadLogo\" align=\"right\"></td>" +
"      </tr>" +
"    </tbody>" +
"  </table>" +
"" +
"  <table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\"" +
"         style=\"border-bottom: 1px solid white;\" bgcolor=\"#0A6CCE\">" +
"    <tbody>" +
"      <tr>" +
"        <td height=\"20\" valign=\"middle\" nowrap=\"nowrap\" class=" +
"        \"mnpLocalToolbar\" style=\"color: rgb(255, 255, 255);\"" +
"            hover=\"#FFCC00\">&nbsp;<a style=" +
"            \"color: rgb(255, 255, 255); text-decoration: none;\" dir=" +
"            \"ltr\" href=\"../index.html\" target=" +
"            \"_parent\">Microsoft Home</a>&nbsp;&nbsp;|&nbsp;<a style=" +
"            \"color: rgb(255, 255, 255); text-decoration: none;\" dir=" +
"            \"ltr\" href=\"../msn/index.html\" target=\"_parent\" guid=" +
"            \"m4cd003c10a1e3c2bbd388c636326cea5\">MSN" +
"            Home</a>&nbsp;&nbsp;|&nbsp;<a style=\"color: rgb(255, 255, 255); text-decoration: none;\"" +
"           dir=\"ltr\" href=" +
"           \"../admin/index.html\"" +
"           target=\"_parent\" guid=" +
"           \"m8f1bb1bde0e14e99e6950e4b7ec6483b\">Manage Our" +
"           Employees</a>&nbsp;&nbsp;</td>" +
"      </tr>" +
"    </tbody>" +
"  </table>" +
"" +
"  <table cellpadding=\"0\" cellspacing=\"0\" border=\"0\" width=\"100%\"" +
"  dir=\"ltr\">" +
"    <tbody>" +
"      <tr valign=\"top\">" +
"        <td width=\"100%\" dir=\"ltr\">" +
"          <div id=\"divContent\">" +
"            <div style=" +
"            \"border-bottom: 1px solid rgb(102, 153, 204); padding: 0px 10px;\">" +
"            <img border=\"0\" alt=\"Search Microsoft.com\" width=\"700\"" +
"                   height=\"27\" src=\"subbanner.gif\">" +
"            </div><a name=\"mainContent\"></a>" +
body +
"          </div>" +
"        </td>" +
"      </tr>" +
"    </tbody>" +
"  </table>" +
"" +
"  <table cellpadding=\"0\" cellspacing=\"0\" width=\"100%\" border=\"0\"" +
"         bgcolor=\"#0A6CCE\" style=\"color: rgb(255, 255, 255);\" dir=" +
"         \"ltr\">" +
"    <tbody>" +
"      <tr>" +
"        <td class=\"mnpFooterTopRow\" nowrap=\"nowrap\" height=\"20\">" +
"        &nbsp;<a href=" +
"        \"mailto:gates@microsoft.com\"" +
"           target=\"_parent\" style=" +
"           \"color: rgb(255, 255, 255); text-decoration: none;\"" +
"           onmouseout=\"mnpFooterMouse(this, '#FFFFFF')\"" +
"           onmouseover=\"mnpFooterMouse(this, '#FFCC00')\">Contact" +
"           Us</a>&nbsp;|&nbsp;<a href=" +
"           \"../about/gpl.html\"" +
"           target=\"_parent\" style=" +
"           \"color: rgb(255, 255, 255); text-decoration: none;\"" +
"           onmouseout=\"mnpFooterMouse(this, '#FFFFFF')\"" +
"           onmouseover=\"mnpFooterMouse(this, '#FFCC00')\">Legal</a>&nbsp;</td>" +
"      </tr>" +
"" +
"      <tr>" +
"        <td class=\"mnpFooterBottomRow\" nowrap=\"nowrap\" height=\"30\">" +
"        <font color=\"#ffffff\">&nbsp;<span dir=" +
"        \"ltr\">2003 Microsoft Corporation. All rights" +
"        reserved.</span>&nbsp;<a href=" +
"        \"../about/gpl.html\"" +
"           target=\"_parent\" style=\"color: rgb(255, 255, 255);\"" +
"           onmouseout=\"mnpFooterMouse(this, '#FFFFFF')\"" +
"           onmouseover=\"mnpFooterMouse(this, '#FFCC00')\">Terms of" +
"           Use</a>&nbsp;</font></td>" +
"      </tr>" +
"    </tbody>" +
"  </table>" +
"" +
"  <layer visibility=\"hide\"></layer>" +
"" +
"  <div style=\"display: none;\">" +
"    <img width=\"0\" height=\"0\" border=\"0\" hspace=\"0\" vspace=\"0\"" +
"         src=\"trans_pixel.gif\">" +
"  </div>" +
"</body>" +
"</html>"
    );
  }
}

