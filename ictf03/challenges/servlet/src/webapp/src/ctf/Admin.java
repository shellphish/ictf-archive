/**
 * CTF search admin servlet.
 */

package ctf;

import java.io.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;

/**
 * Administration servlet.
 */
public final class Admin
  extends HttpServlet
{
  /**
   * Handle GET request.
   *
   * @param req Request.
   * @param resp Response.
   * @throws IOException If an I/O error occurs.
   * @throws ServletException If a servlet error occurs.
   */
  public void doGet(HttpServletRequest req, HttpServletResponse resp)
    throws IOException, ServletException
  {
    handleRequest(req, resp);
  }

  /**
   * Handle POST request.
   *
   * @param req Request.
   * @param resp Response.
   * @throws IOException If an I/O error occurs.
   * @throws ServletException If a servlet error occurs.
   */
  public void doPost(HttpServletRequest req, HttpServletResponse resp)
    throws IOException, ServletException
  {
    handleRequest(req, resp);
  }

  /**
   * Handle request.
   *
   * @param req Request.
   * @param resp Response.
   * @throws IOException If an I/O error occurs.
   * @throws ServletException If a servlet error occurs.
   */
  public void handleRequest(HttpServletRequest req, HttpServletResponse resp)
    throws IOException, ServletException
  {
    try {
      Page page = null;
      HttpSession session = null;
      Database db = new Database();
      String action = req.getParameter("action");
  
      /* Check for login */
      if (action != null && action.equals("doLogin")) {
        if (isAuthorized(req))
          session = req.getSession();
        else
          page = getLoginFailurePage(req, resp, db);
      } else {
        session = req.getSession(false);
      }
  
      /* Perform actions and get page */
      if (session != null) {
        if (action != null) {
          if (action.equals("doLogout")) {
            session.invalidate();
            page = getLoginPage(req, resp, db);
          } else if (action.equals("addArticle")) {
            addArticle(req, db);
          } else if (action.equals("deleteArticles")) {
            deleteArticles(req, db);
          } else if (action.equals("updateArticle")) {
            updateArticle(req, db);
          }
        }
  
        if (page == null)
          page = getAdminIndex(req, resp, db);
      }
  
      if (page == null)
        page = getLoginPage(req, resp, db);
  
      page.output();
    } catch (DatabaseException e) {
      throw new ServletException(e);
    }
  }

  /**
   * Check password.
   *
   * @param p Password.
   * @return True if valid, otherwise false.
   */
  protected boolean checkPassword(String p)
  {
    byte[] b = p.getBytes();

    for (int i = 0; i < b.length; i++)
      b[i] = (byte) (b[i] + 1);

    String tmp = new String(b);

    return tmp.equals("@@SERVLET_PASSWORD@@");
  }

  /**
   * Check authorization.
   *
   * @param req Request.
   * @return True if authorized, otherwise false.
   */
  protected boolean isAuthorized(HttpServletRequest req)
  {
    String username = req.getParameter("username");
    String password = req.getParameter("password");

    if (username == null || password == null ||
      !checkPassword(password))
      return false;

    return true;
  }

  /**
   * Add an article.
   *
   * @param req Request.
   * @param db Database.
   * @throws DatabaseException If unable to add article.
   */
  protected void addArticle(HttpServletRequest req, Database db)
    throws DatabaseException
  {
    String title = req.getParameter("title");
    String text = req.getParameter("article");

    if (title != null && text != null)
      db.addArticle(title, text);
  }

  /**
   * Delete articles.
   *
   * @param req Request.
   * @param db Database.
   * @throws DatabaseException If unable to delete articles.
   */
  protected void deleteArticles(HttpServletRequest req, Database db)
    throws DatabaseException
  {
    List l = new LinkedList();
    String[] values = req.getParameterValues("article");

    if (values == null)
      return;

    for (int i = 0; i < values.length; i++)
      l.add(new Integer(Integer.parseInt(values[i])));

    db.deleteArticles(l);
  }

  /**
   * Update articles.
   *
   * @param req Request.
   * @param db Database.
   * @throws DatabaseException If unable to update article.
   */
  protected void updateArticle(HttpServletRequest req, Database db)
    throws DatabaseException
  {
    String title = req.getParameter("title");
    String keywords = req.getParameter("keywords");

    if (title == null || keywords == null ||
      title.equals("") || keywords.equals(""))
      return;

    db.updateArticle(keywords, title);
  }

  /**
   * Return login page.
   *
   * @param req Request.
   * @param resp Response.
   * @param db Database.
   */
  protected Page getLoginPage(HttpServletRequest req,
    HttpServletResponse resp, Database db)
  {
    String loginBody =
"<table cellpadding=\"20\" width=\"100%\"><tr><td>\n" +
"<h2>Search Administration Login</h2>" +
"Unauthorized access to Microsoft's knowledge base administration " +
"interface is punishable to the full extent of the power of a " +
"modern monopoly, so no funny stuff.\n" +
"<br/><br/>\n" +
"<form class=\"form\" action=\"" +
req.getContextPath() + req.getServletPath() +
"\" method=\"get\">\n" +
"<div class=\"fieldDesc\"><b>Username</b></div>\n" +
"<input type=\"text\" name=\"username\" size=\"10\"/>\n" +
"<br/><br/>\n" +
"<div class=\"fieldDesc\"><b>Password</b></div>\n" +
"<input type=\"password\" name=\"password\" size=\"10\"/>\n" +
"<br/><br/>\n" +
"<input type=\"hidden\" name=\"action\" value=\"doLogin\"/>\n" +
"<input type=\"submit\" name=\"login\" value=\"Login\"/>\n" +
"</form></td></tr></table>\n";

    return new Page(req, resp, "Administration", loginBody);
  }

  /**
   * Return login failure page.
   *
   * @param req Request.
   * @param resp Response.
   * @param db Database.
   */
  protected Page getLoginFailurePage(HttpServletRequest req,
    HttpServletResponse resp, Database db)
  {
    String failureBody =
"<table cellpadding=\"20\" width=\"100%\"><tr><td>\n" +
"<h2>Support Administration Login Failed</h2>\n" +
"Please remain at your computer. Representatives of Microsoft Corporation " +
"are currently triangulating your geographical position " +
"and will be arriving shortly. Do not attempt to flee.\n" +
"</td></tr></table>\n";

    return new Page(req, resp, "Login Failed", failureBody);
  }

  /**
   * Return administration index.
   *
   * @param req Request.
   * @param resp Response.
   * @param db Database.
   * @throws DatabaseException If unable to get articles.
   */
  protected Page getAdminIndex(HttpServletRequest req,
    HttpServletResponse resp, Database db)
    throws DatabaseException
  {
    List articles = db.getArticles();

    String indexBody =
"<table cellpadding=\"20\" width=\"100%\"><tr><td>\n" +
"<h2>Add New Knowledge Base Article</h2>\n" +
"<form class=\"form\" action=\"" +
req.getContextPath() + req.getServletPath() +
"\" method=\"get\">\n" +
"<div class=\"fieldDesc\">\n" +
"<b>Title</b>\n" +
"</div>\n" +
"<input type=\"text\" name=\"title\" size=\"60\"/>\n" +
"<br/><br/>\n" +
"<div class=\"fieldDesc\">\n" +
"<b>Article Text</b>\n" +
"</div>\n" +
"<textarea name=\"article\" rows=\"15\" cols=\"60\"></textarea>\n" +
"<br/><br/>\n" +
"<input type=\"hidden\" name=\"action\" value=\"addArticle\"/>\n" +
"<input type=\"submit\" name=\"addArticle\" value=\"Add Article\"/>\n" +
"</form><br/><br/>\n" +
"<h2>Current Knowledge Base Articles</h2>\n" +
"<form class=\"form\" action=\"" +
req.getContextPath() + req.getServletPath() +
"\" method=\"get\">\n" +
"<table class=\"genericTable\">\n" +
"<tr>\n" +
"<th>Select?</th>\n" +
"<th>Title</th>\n" +
"</tr>\n";

    Iterator it = articles.iterator();
    while (it.hasNext()) {
      Article a = (Article) it.next();
      indexBody +=
"<tr>\n" +
"<td><input type=\"checkbox\" name=\"article\" value=\"" + a.id + "\"/></td>\n" +
"<td>" + a.title + "</td>\n" +
"</tr>\n";
    }

    indexBody +=
"</table>\n" +
"<br/>\n" +
"<input type=\"hidden\" name=\"action\" value=\"deleteArticles\"/>\n" +
"<input type=\"submit\" name=\"deleteArticles\" value=\"Delete Selected\"/>\n" +
"</form><br/><br/>\n" +
"<form class=\"form\" action=\"" +
req.getContextPath() + req.getServletPath() +
"\" method=\"get\">\n" +
"<input type=\"submit\" name=\"doLogout\" value=\"Logout\"/>\n" +
"<input type=\"hidden\" name=\"action\" value=\"doLogout\"/>\n" +
"</form>\n" +
"</td></tr></table>\n";

    return new Page(req, resp, "Administration", indexBody);
  }
}

