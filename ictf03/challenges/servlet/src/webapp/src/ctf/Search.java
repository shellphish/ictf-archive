/**
 * CTF BassTard help search servlet.
 */

package ctf;

import java.io.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;

public final class Search
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
   * Return index page.
   *
   * @param req Request.
   * @param resp Response.
   * @param db Database.
   */
  protected Page getIndexPage(HttpServletRequest req,
    HttpServletResponse resp, Database db)
  {
    String body =
"            <form style=\"margin-top: 0px; margin-bottom: 0px;\"" +
"                  name=\"frmS\" method=\"get\" action=\"?\"" +
"                  >" +
"              <input type=\"hidden\" name=\"action\" value=\"doSearch\"/>\n" +
"              <input type=\"hidden\" name=\"st\" value=" +
"                    \"b\"><input type=\"hidden\" name=\"na\" value=\"80\">" +
"" +
"              <div style=\"text-align: center; margin-top: 29px;\">" +
"                <div class=\"bSearchDiv\">" +
"                  <div class=\"hdr1\" style=\"margin-bottom: 2px;\">" +
"                    Search Microsoft.com for" +
"                  </div>" +
"" +
"                  <table cellspacing=\"0\" cellpadding=\"0\">" +
"                    <tbody>" +
"                      <tr valign=\"bottom\">" +
"                        <td><input size=\"28\" class=\"bFrmTxt\"" +
"                               name=\"keywords\" maxlength=\"255\" value=" +
"                               \"\"></td>" +
"" +
"                        <td><img src=\"trans.gif\" alt=\"\" width=\"6\"" +
"                        height=\"1\" border=\"0\"><input style=" +
"                        \"padding: 0px 1px 0px 2px; font-weight: normal; font-size: 70%; font-family: Tahoma,Arial;\"" +
"                               id=\"GoButton1\" type=\"submit\" value=" +
"                               \"Go\"><img src=\"trans.gif\" alt=\"\"" +
"                               width=\"12\" height=\"1\" border=" +
"                               \"0\"></td>" +
"" +
"                        <td>" +
"                        </td>" +
"                      </tr>" +
"                    </tbody>" +
"                  </table>" +
"" +
"                  <div class=\"bTipTextQueryDiv\" style=" +
"                  \"margin-bottom: 28px;\">" +
"                    <span class=\"bodyText2\"><span style=" +
"                    \"font-weight: bold;\">Tip:</span>&nbsp;<span style=\"font-weight: normal;\">" +
"                    For better results, try entering more words." +
"                    Example: <i>directx 9.0 downloads</i> instead" +
"                    of simply <i>directx</i></span></span>" +
"                  </div>" +
"                </div>" +
"              </div>" +
"" +
"              <div style=\"text-align: center;\">" +
"                <div class=\"bSearchDiv\" style=\"padding-top: 3px;\">" +
"                  <hr class=\"gray\">" +
"" +
"                  <table cellspacing=\"0\" cellpadding=\"0\"" +
"                         style=\"margin-top: 8px;\">" +
"                    <tbody>" +
"                      <tr>" +
"                        <td><img border=\"0\" width=\"28\" height=\"28\"" +
"                        alt=\"\" src=\"msn.gif\"></td>" +
"" +
"                        <td><img height=\"1\" width=\"6\" alt=\"\"" +
"                             src=\"trans.gif\"></td>" +
"" +
"                        <td>" +
"                          <div class=\"hdr1\">" +
"                            Or search the entire Internet with a " +
"			    decent search engine" +
"                          </div><span class=" +
"                             \"bodyText1\"><a class=\"inline\" na=\"70\"" +
"                             href=\"http://google.com/\">Try Google" +
"                             Search</a></span>" +
"                        </td>" +
"                      </tr>" +
"                    </tbody>" +
"                  </table>" +
"                </div>" +
"              </div>" +
"            </form>";

    return new Page(req, resp, "Search Microsoft.com", body);
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
   * Return results page.
   *
   * @param req Request.
   * @param resp Response.
   * @param db Database.
   * @throws DatabaseException If unable to get results.
   */
  protected Page getResultsPage(HttpServletRequest req,
    HttpServletResponse resp, Database db)
    throws DatabaseException
  {
    List results = db.searchArticles(req.getParameter("keywords"));
    Iterator it = results.iterator();

    String body =
"            <form style=\"margin-top: 0px; margin-bottom: 0px;\"" +
"                  name=\"frmS\" method=\"get\" action=\"?\"" +
"                  >" +
"              <input type=\"hidden\" name=\"action\" value=\"doSearch\"/>\n" +
"              <div style=\"text-align: center; margin-top: 29px;\">" +
"                <div class=\"bSearchDiv\">" +
"                  <div class=\"hdr1\" style=\"margin-bottom: 2px;\">" +
"                    Search Microsoft.com" +
"                  </div>" +
"                  <table cellspacing=\"0\" cellpadding=\"0\">" +
"                    <tbody>" +
"                      <tr valign=\"bottom\">" +
"                        <td><input size=\"28\" class=\"bFrmTxt\"" +
"                               name=\"keywords\" maxlength=\"255\" value=" +
"                               \"\"></td>" +
"" +
"                        <td><img src=\"trans.gif\" alt=\"\" width=\"6\"" +
"                        height=\"1\" border=\"0\"><input style=" +
"                        \"padding: 0px 1px 0px 2px; font-weight: normal; font-size: 70%; font-family: Tahoma,Arial;\"" +
"                               id=\"GoButton1\" type=\"submit\" value=" +
"                               \"Go\"><img src=\"trans.gif\" alt=\"\"" +
"                               width=\"12\" height=\"1\" border=" +
"                               \"0\"></td>" +
"" +
"                        <td>" +
"                        </td>" +
"                      </tr>" +
"                    </tbody>" +
"                  </table>" +
"                  <div class=\"bTipTextQueryDiv\" style=" +
"                  \"margin-bottom: 28px;\">" +
"                    <span class=\"bodyText2\"><span style=" +
"                    \"font-weight: bold;\">Tip:</span>&nbsp;<span style=\"font-weight: normal;\">" +
"                    For better results, try entering more words." +
"                    Example: <i>directx 9.0 downloads</i> instead" +
"                    of simply <i>directx</i></span></span>" +
"                  </div>" +
"                  <div class=\"hdr1\" style=\"margin-bottom: 2px;\">" +
"                    " + results.size() + " results found." +
"                  </div>" +
"                  <table cellspacing=\"0\" cellpadding=\"0\">" +
"                    <tbody>";

    while (it.hasNext()) {
      Article a = (Article) it.next();

      body +=
"                      <tr valign=\"bottom\">" +
"                      <td><a href=\"http://google.com/search?q=" +
a.title.replaceAll("\"", "%22") +
"+site%3Amicrosoft.com\">" + a.title + "</a><br/>\n" +
"                      " + a.text.replaceAll("\n\n", "<br/><br/>") +
"<br/><br/></td>\n" +
"                      </tr>";
    }

    body +=
"                    </tbody>" +
"                  </table>" +
"                </div>" +
"              </div>" +
"              <div style=\"text-align: center;\">" +
"                <div class=\"bSearchDiv\" style=\"padding-top: 3px;\">" +
"                  <hr class=\"gray\">" +
"                  <table cellspacing=\"0\" cellpadding=\"0\"" +
"                         style=\"margin-top: 8px;\">" +
"                    <tbody>" +
"                      <tr>" +
"                        <td><img border=\"0\" width=\"28\" height=\"28\"" +
"                        alt=\"\" src=\"msn.gif\"></td>" +
"" +
"                        <td><img height=\"1\" width=\"6\" alt=\"\"" +
"                             src=\"trans.gif\"></td>" +
"" +
"                        <td>" +
"                          <div class=\"hdr1\">" +
"                            Search the entire Internet with a " +
"			    decent search engine (or help us <a href=\"/servlet\">improve our own</a>)" +
"                          </div><span class=" +
"                             \"bodyText1\"><a class=\"inline\" na=\"70\"" +
"                             href=\"http://google.com/\">Try Google" +
"                             Search</a></span>" +
"                        </td>" +
"                      </tr>" +
"                    </tbody>" +
"                  </table>" +
"                </div>" +
"              </div>" +
"            </form>";

    return new Page(req, resp, "Search Results", body);
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
      Database db = new Database();
      String action = req.getParameter("action");

      if (action != null) {
        if (action.equals("doSearch"))
          page = getResultsPage(req, resp, db);
      }

      if (page == null)
        page = getIndexPage(req, resp, db);

      page.output();
    } catch (DatabaseException e) {
      throw new ServletException(e);
    }
  }
}

