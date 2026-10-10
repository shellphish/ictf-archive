import com.gargoylesoftware.htmlunit.*;
import com.gargoylesoftware.htmlunit.html.*;
import org.apache.commons.codec.*;
import java.io.*;
import java.util.*;

public class FriendshipAcceptor {
  public static void main(String[] args) {
    try {
      WebClient webClient = new WebClient(BrowserVersion.INTERNET_EXPLORER_7);
      HtmlPage page = webClient.getPage("http://m.facebook.com/reqs.php");
      HtmlForm form = (HtmlForm)((ArrayList)page.getForms()).get(0);
      
      HtmlTextInput emailField = form.getInputByName("email");
      emailField.setValueAttribute(args[0]);
      HtmlPasswordInput passwordField = form.getInputByName("pass");
      passwordField.setValueAttribute(args[1]);
      HtmlSubmitInput button = form.getInputByValue("Log In");
      HtmlPage page2 = button.click();
      
      List<HtmlAnchor> anchorList = page2.getAnchors();
      /*Iterator iter = anchorList.iterator();
      while(iter.hasNext()) {
	HtmlAnchor item = (HtmlAnchor)iter.next();
	if(item.toString().lastIndexOf(args[2]) > 0 ) {
	  HtmlPage page3 = (HtmlPage)item.openLinkInNewWindow();
	  List<HtmlAnchor> anchorList2 = page3.getAnchors();
	  Iterator iter2 = anchorList2.iterator();
	  while(iter2.hasNext()) {
	    HtmlAnchor item2 = (HtmlAnchor)iter2.next();
	    if(item2.toString().lastIndexOf("addfriend") > 0 ) {
	      System.out.println(item2);
	      page3 = item2.click();
	      form = (HtmlForm)((ArrayList)page3.getForms()).get(0);
	      System.out.println(form);
	      button = form.getInputByValue("Connect");
	      button.click();
	      break;
	    }
	  }
	}
      }*/
      List<HtmlForm> forms = page2.getForms();
      Iterator iter = forms.iterator();
      while(iter.hasNext()) {
        form = (HtmlForm)iter.next();
	try {
	  button = form.getInputByName("confirm");
	  button.click();
	}
	catch(Exception e) {
	}
      }
    }
    catch(IOException ioe) {
      ioe.printStackTrace();
    }
  }
}
