/**
 * Database interface.
 */

package ctf;

import java.sql.*;
import java.util.*;

/**
 * Database exception.
 */
class DatabaseException
  extends Exception
{
  /**
   * Create a new database exception.
   *
   * @param reason Reason.
   */
  public DatabaseException(Throwable reason)
  {
    super(reason);
  }
}

/**
 * Article.
 */
final class Article
{
  /** ID */
  public final int id;

  /** Title */
  public final String title;

  /** Text */
  public final String text;

  /**
   * Create new article.
   *
   * @param i ID.
   * @param t Title.
   * @param x Text.
   */
  public Article(int i, String t, String x)
  {
    id = i;
    title = t;
    text = x;
  }
}

/**
 * Bass Tard database interface.
 */
public final class Database
{
  /** Connection */
  private Connection conn;

  /**
   * Create a new database interface.
   *
   * @throws DatabaseException If unable to connect.
   */
  public Database()
    throws DatabaseException
  {
    try {
      Class.forName("org.postgresql.Driver").newInstance();
      conn = DriverManager.getConnection("jdbc:postgresql://localhost/kb?" +
        "user=kb&password=@@SERVLET_DBPASSWORD@@");
    } catch (Exception e) {
      throw new DatabaseException(e);
    }
  }

  /**
   * Return current articles.
   *
   * @return Articles.
   * @throws DatabaseException If unable to retrieve articles.
   */
  public List getArticles()
    throws DatabaseException
  {
    try {
      List l = new LinkedList();
      Statement s = conn.createStatement();
      ResultSet r = s.executeQuery("select * from kb order by title");

      while (r.next())
        l.add(new Article(r.getInt("id"),
				  r.getString("title"), r.getString("info")));

      r.close();

      return l;
    } catch (Exception e) {
      throw new DatabaseException(e);
    }
  }

  /**
   * Add an article.
   *
   * @param title Title.
   * @param text Text.
   * @throws DatabaseException If unable to add article.
   */
  public void addArticle(String title, String text)
    throws DatabaseException
  {
    try {
      Statement s = conn.createStatement();
      s.execute("insert into kb(title, info) values('" +
        escape(title) + "', '" + escape(text) + "')");
    } catch (Exception e) {
      throw new DatabaseException(e);
    }
  }

  /**
   * Delete articles.
   *
   * @param ids List of IDs.
   * @throws DatabaseException If unable to delete articles.
   */
  public void deleteArticles(List ids)
    throws DatabaseException
  {
    try {
      if (ids.size() <= 0)
        return;

      Iterator it = ids.iterator();
      String str = "delete from kb where ";

      while (it.hasNext()) {
        str += "id = '" + escape(it.next().toString()) + "' ";
        if (it.hasNext())
          str += "or ";
      }

      Statement s = conn.createStatement();
      s.execute(str);
    } catch (Exception e) {
      throw new DatabaseException(e);
    }
  }

  /**
   * Update article.
   *
   * @param keywords Keywords.
   * @param title Title.
   * @throws DatabaseException If unable to update article.
   */
  public void updateArticle(String keywords, String title)
    throws DatabaseException
  {
    try {
      String str = "update kb set title = '" + escape(title) +
        "' where title like '%" + escape(keywords) + "%'";

      Statement s = conn.createStatement();
      s.execute(str);
    } catch (Exception e) {
      throw new DatabaseException(e);
    }
  }

  /**
   * Search articles.
   *
   * @param keywords Keywords.
   * @return Articles.
   * @throws DatabaseException If unable to search articles.
   */
  public List searchArticles(String keywords)
    throws DatabaseException
  {
    try {
      String str = "select * from kb ";

      if (keywords != null && !keywords.equals("")) {
        str += "where ";

        StringTokenizer t = new StringTokenizer(keywords);

        while (t.hasMoreTokens()) {
          str += "title like '%" + escape(t.nextToken()) + "%' ";

				  if (t.hasMoreTokens())
					  str += " and ";
        }
      }

      str += " order by title";

      Statement s = conn.createStatement();
      ResultSet r = s.executeQuery(str);
      List l = new LinkedList();

      while (r.next())
        l.add(new Article(r.getInt("id"),
          r.getString("title"), r.getString("info")));

      return l;
    } catch (Exception e) {
      throw new DatabaseException(e);
    }
  }

	/**
	 * Escape SQL.
	 *
	 * @param str String to escape.
	 * @return Escaped string.
	 */
	public static String escape(String str)
	{
		return str.replaceAll("'", "''");
	}
}

