import com.gargoylesoftware.htmlunit.*;
import com.gargoylesoftware.htmlunit.html.*;
import org.apache.commons.codec.*;
import java.io.*;
import java.util.*;

public class CheckProfiles {
  public static void main(String[] args) {
    try {
      WebClient webClient = new WebClient(BrowserVersion.INTERNET_EXPLORER_7);
      System.out.println("http://127.0.0.1?session="+args[0]);
      HtmlPage page = webClient.getPage("http://127.0.0.1?session="+args[0]);
      HtmlForm form = (HtmlForm)((ArrayList)page.getForms()).get(0);
      
      HtmlTextInput emailField = form.getInputByName("username");
      emailField.setValueAttribute("bironulesk");
      HtmlPasswordInput passwordField = form.getInputByName("password");
      passwordField.setValueAttribute("god");
      HtmlSubmitInput button = form.getInputByName("submit");
      HtmlPage page2 = button.click();

      int i = 0;
      for(i = 1;i < args.length;i++) {
         try { 
         HtmlPage page3 = webClient.getPage(args[i]);
         }
         catch(Exception e){
         }
      }
      
      HtmlPage page4 = webClient.getPage("http://127.0.0.1/logout");

    } 
    catch(Exception ioe) {
    }
  }
}
