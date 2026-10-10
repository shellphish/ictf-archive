#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <cmath>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include "cgicc/Cgicc.h"
#include "cgicc/HTTPHTMLHeader.h"
#include "cgicc/HTMLClasses.h"
#include <boost/format.hpp>
#include "boost/filesystem/operations.hpp" 
#include "boost/filesystem/path.hpp"
#include "boost/filesystem/fstream.hpp"    
#include <sstream>
#include "boost/tuple/tuple.hpp"
#include "boost/tuple/tuple_io.hpp"
#include <cstdio>
#include "boost/lexical_cast.hpp"
#include "boost/date_time/posix_time/posix_time.hpp"
#include "boost/date_time/local_time_adjustor.hpp"
#include "boost/date_time/c_local_time_adjustor.hpp"
#include "boost/date_time/local_time/local_time.hpp"
#include <boost/regex.hpp>
#include <iterator>


namespace fs=boost::filesystem;                   
using boost::format;

using namespace boost::tuples;

using namespace std;
using namespace cgicc;

typedef void(*action_ptr)(Cgicc &);
typedef boost::tuple<action_ptr,string> dir_tuple;
typedef boost::tuple<double,double,string> stock_tuple;

#define TEAM_BOX

static const int CHECK_LEN=172;
static const string PASSWORD_FILENAME="secret.txt";
static const string DEPOSIT_FILENAME="deposit.txt";
static const string COOKIE_NAME="stocks";


#ifndef TEAM_BOX
#else
static const string CHECK_CHECKER_BIN="/usr/bin/ccheck";
static const string ACCOUNT_DIR="/home/sts/accounts";
static const string COMMENT_DIR="/home/sts/comments";
static const string TRANSACTION_DIR="/var/spool/transactions/sts";
#endif


static const string header_html="<html>\n" \
"  <head>\n" \
"    <link href=\"../style/hbbank.css\" rel=\"stylesheet\" type=\"text/css\" />\n" \
"    <title>The Hillbilly Stocks Market</title>\n" \
"  </head>\n" \
"  <body>\n" \
"    <div id=\"page\">\n" \
"      <div id=\"header\">\n" \
"        <h1>Hillbilly stocks market</h1>\n" \
"      </div>\n" \
"      <div id=\"navigation\">\n" \
"        <ul>" \
"          <li id=\"home\"><a href=\"stocks?action=index_page\">Home</a></li>\n" \
"          <li id=\"home\"><a href=\"stocks?action=login\">Login</a></li>\n" \
"          <li id=\"home\"><a href=\"stocks?action=logout\">Logout</a></li>\n" \
"        </ul>\n" \
"      </div>\n" \
"      <div id=\"content\">\n";
 
string trailer_html="      </div>\n" \
"      <div id=\"footer\">\n" \
"        <hr />\n" \
"        [<a href=\"stocks?action=index_page\">The Hillbilly Stocks Market</a>]<br />\n" \
"      </div>\n" \
"    </div>\n";


std::map<string, dir_tuple > directory_map;
std::map<string, stock_tuple > stocks_map;

static const double alpha=1.0; 

static const int IBAN_LEN=172;
//XXX fix me, phi filled with a random number TB deleted before image is crafted
int phi;

bool get_cookieval(const Cgicc & cgi,string & uname, string & password);
void browse_value(Cgicc & cgi);

void greets(const Cgicc & cgi)
{
  string username,password;
  get_cookieval(cgi,username,password);
  if (username!="")
    cout<<span("Howdy "+username+"!" ).set("style","color:red")<<br()<<br()<<endl;      
}

/* We don't want nasty cross site scripting */
string sanitize(const string & s)
{
  boost::regex e("(<script([^>])+>)|(</script>)");

  std::ostringstream t(std::ios::out | std::ios::binary);
  std::ostream_iterator<char, char> oi(t);
  boost::regex_replace(oi, s.begin(), s.end(),
		       e,"", boost::match_default);
  return t.str();
}

/* next version will be better randomized*/
double f(int t)
{
  return 2.0 + (sin((double(t)/22.5)*atan(1.0)));
}


bool is_valid_user(const Cgicc & cgi);

void index_page(const Cgicc & cgi,bool next_time=true)
{
  string uname,password;
  get_cookieval(cgi,uname,password);
  cout<<"<p>This is the Hillbilly stock market service."\
    "We have stocks, we sell it to you,so you can buy stock from us. "\
    "Actually we don't know what stocks are. So we sell banjos, moonshine clay jugs, and pipes. "\
    "Not all the pipes though. Only corncob ones, couse they are the best.<p>"\
    "<p>You have to login to do some of the stuff that needs to be done "\
    "and to logout afterwards. Then you can login again. And, of course, logout.</p>"\
    "Check out what wonderful services we have! You can for instance: ";
  cout<<ul();
  for(typeof(directory_map.begin()) i= directory_map.begin();i!=directory_map.end();++i)
    if (i->first!="login" && i->first!="logout")
      cout<<li(a(get<1>(i->second)).set("href","stocks?action="+i->first) );
  cout<<ul();
}


void send_header(const Cgicc  cgi, const string * cookie=NULL  )
{
  static bool header_sent=0;
  
  if (header_sent) return;

  if (cookie==NULL)
    {
      cout << HTTPHTMLHeader() << endl;
    }
  else
    {  
      HTTPHTMLHeader h;
      h.setCookie((HTTPCookie(COOKIE_NAME, *cookie)));
      cout<<h;
    }
  // Set up the HTML document
  cout << html() << head(title("Stock service")) << endl;
  cout << body() <<endl;
  cout<< header_html;
  greets(cgi);

  cout<<endl;
  header_sent++;
}

vector<pair<string, string> > & unset_cookies( vector<pair<string, string> > &v)
{
  v.push_back(pair<string,string>(COOKIE_NAME,""));
  return v;
}

bool is_valid_user(const string & uname, const string& password)
{

  string filename=(format("%s/%s/%s")%ACCOUNT_DIR%uname%PASSWORD_FILENAME).str();
    if (fs::exists(fs::path((filename))))
    {
      string local_password;
      fs::ifstream secret(filename);
      secret>>local_password;
      secret.close();
      if (local_password==password)
	  return true;
	
    }
    
  return false;
}

bool get_cookieval(const Cgicc & cgi,string & uname, string & password)
{
  string result="";
  const CgiEnvironment& env = cgi.getEnvironment();
  const_cookie_iterator i;
  for(i = env.getCookieList().begin(); i != env.getCookieList().end(); ++i) {
    if(i->getName()==COOKIE_NAME)
      result=i->getValue();
  }

  uname=result.substr(0,result.find(':',0));
  password=result.substr(result.find(':',0)+1);
  
  
  return result==""?false:true;
}

bool is_valid_user(const Cgicc & cgi)
{
  string uname,password;
  get_cookieval(cgi,uname,password);
  if (uname!="" && password != "")
    {
      if (is_valid_user(uname,password))
	  return true;
      else
	{
	  string cookie="";
	  send_header(cgi,&cookie);
	}
    }
  return false;
}


void error(string s)
{
  cout<<span(s).set("style","color:red")<<endl;
}

void success(string s)
{
  cout<<span(s).set("style","color:green")<<endl;
}


typedef tuple<string,string,string> field_info;

bool data_form(const Cgicc & cgi,const string & action, vector<field_info> & fields , int& sentinel, bool textarea_flag=false)
{
  ++sentinel;
  const_form_iterator subaction = cgi.getElement("do");
  
  if(subaction == cgi.getElements().end() || **subaction!="submit" || sentinel) {
    send_header(cgi);
    cout<<form().set("method","post").set("action","stocks")<<endl;
    cout<<fieldset()<<endl;
    cout<<legend(get<1>(directory_map[action]))<<table()<<endl;
    for(vector<field_info>::const_iterator i=fields.begin();i!=fields.end();++i)
      cout<<tr()<<td(get<0>(*i))<<td()<<input().set("type", get<1>(*i) ).set("name",get<2>(*i))<<td()<<tr();
    cout<<table()<<endl;
    if (textarea_flag) //awful hack...
      cout<<textarea("This service is awesome").set("cols","40").set("rows","5").set("name","comment")<<br();
    cout<<input().set("type","hidden").set("name","action").set("value",action);
    cout<<input().set("type","hidden").set("name","do").set("value","submit");
    cout<<input().set("type","submit").set("value","submit");
    cout<<fieldset()<<endl;
    cout<<form()<<br();
    return true;
  }
  return false;

}

bool data_present(const Cgicc cgi, vector<string>& v)
{
  const_form_iterator userdata;
  for(vector<string>::iterator i=v.begin();i!=v.end();++i)
    {
      userdata = cgi.getElement(*i);      
      if(userdata != cgi.getElements().end() && **userdata!="")
	  *i=**userdata;	  
      else
	{
	  send_header(cgi);
	  error("Some of the fields are missing or empty");
	  return false;
	}
	
    }
  return true;
}


void login(Cgicc & cgi)
{
  vector<field_info> tmp_v;
  tmp_v.push_back(field_info("Username:","text","username"));
  tmp_v.push_back(field_info("Password:","password","password"));
  static int sentinel=-1;

  if (data_form(cgi,"login",tmp_v,sentinel));
  else 
      {
	vector<string> tmp_v;
	tmp_v.push_back("username");
	tmp_v.push_back("password");

	if (data_present(cgi,tmp_v))
	  {
	    if (is_valid_user(tmp_v[0],tmp_v[1]))
	      {
		string cookie=tmp_v[0]+':'+tmp_v[1];
		send_header(cgi,&cookie);
		success((format("User %s logged in successfully")%tmp_v[0]).str());
		index_page(cgi);
	      }
	    else
	      {
		send_header(cgi);
		error((format("Access denied for user %s")%tmp_v[0]).str());
		login(cgi);
	      }
	    
	  }
      }

  send_header(cgi);		

}
void logout(Cgicc & cgi)
{
  vector<pair<string, string> > v;
  string cookie="";
  send_header(cgi,&cookie);
  string uname,password;
  get_cookieval(cgi,uname,password);
  index_page(cgi);
}
void create_user(Cgicc & cgi)
{

  vector<field_info> tmp_v;
  tmp_v.push_back(field_info("Username:","text","username"));
  tmp_v.push_back(field_info("Password:","password","password"));
  static int sentinel=-1;

  if (data_form(cgi,"create_user",tmp_v,sentinel));
  else 
    {
      vector<string> tmp_v;
      tmp_v.push_back("username");
      tmp_v.push_back("password");
      
      if (data_present(cgi,tmp_v))
	{
	  string user_dir=(format("%s/%s")%ACCOUNT_DIR%tmp_v[0]).str();
	  if (!fs::exists(fs::path(user_dir)))
	    {
	      try
		{
      		  fs::create_directory(user_dir);
		  fs::ofstream secret((format("%s/%s")%user_dir%PASSWORD_FILENAME).str());
		  secret<< tmp_v[1];
		  secret.close();
		  success((format("User %s created successfully")%tmp_v[0]).str());
		}
	      catch(...)
		{
		  cout<<"BOOST:FS returned an error"<<endl;
		}
	    }
	  else
	    error((format("User %s already exists")%tmp_v[0]).str());
	}	   
      else
	create_user(cgi);
    }
  
}

int check_checker(string check)
{

#ifdef TEAM_BOX
  if (check.size()!=CHECK_LEN)
    return -1;
#endif

  static const int BUFFER_LEN=100;
  char buffer[BUFFER_LEN];
  FILE * f=popen((format("%s %s")%CHECK_CHECKER_BIN%check).str().c_str(),"r");
  fgets(buffer,BUFFER_LEN,f);
  pclose(f);
  string result="";
  istringstream is;
  is.str(buffer);
  is>>result;
  return boost::lexical_cast<int>(result);
}


int get_deposit_value(const string & uname)
{
  int amount;
  string filename=(format("%s/%s/%s")%ACCOUNT_DIR%uname%DEPOSIT_FILENAME).str();
  if (fs::exists(fs::path(filename)))
    {
      fs::ifstream deposit_file(filename);
      deposit_file>> amount;
      deposit_file.close();	      
      return amount;
    }
  return 0;
}


int get_stocks_value(const string & uname,int current_timestamp, const string & stock_name)
{
  int amount,stock_timestamp;

  string filename=(format("%s/%s/%s.txt")%ACCOUNT_DIR%uname%(stock_name)).str();
  if (fs::exists(fs::path(filename)))
    {
      fs::ifstream stock_file(filename);
      stock_file>> amount>>stock_timestamp;
      amount=int(double(amount)*(f(int(current_timestamp*get<0>(stocks_map[stock_name])))/f(int(stock_timestamp*get<1>(stocks_map[stock_name]) )))*alpha);
      stock_file.close();	      
      return amount;
    }
  return 0;
}

void deposit(Cgicc & cgi)
{
  if (!is_valid_user(cgi))
    {
      cout<<h2("You need to be logged in to deposit");
      return login(cgi);
    }

  vector<field_info> tmp_v;
  tmp_v.push_back(field_info("Check:","text","check"));
  static int sentinel=-1;

  if (data_form(cgi,"deposit",tmp_v,sentinel))
        cout<<p("Move your money here before if you want to buy some stock!")<<endl;
  else
    {

      vector<string> tmp_vs;
      tmp_vs.push_back("check");
      
      if (data_present(cgi,tmp_vs))
	
	{
	  int amount_num=check_checker(tmp_vs[0]);
	  if (amount_num>=0) // XXX check not valid
	    {

	      time_t timestamp=time(NULL);
	      string uname,passoword;
	      get_cookieval(cgi,uname,passoword);
	      
	      int amount_new= amount_num+get_deposit_value(uname);
	      fs::ofstream deposit_file((format("%s/%s/%s")%ACCOUNT_DIR%uname%DEPOSIT_FILENAME).str());
	      deposit_file<< amount_new<<' '<<timestamp;
	      deposit_file.close();
	      success((format("Deposit of %d$ completed successfully")%amount_num).str());
	      browse_value(cgi);
	    }
	  else
	    {
	      send_header(cgi);
	      error("The check you submitted is not valid");
	      deposit(cgi);
	    }
	}      

    }
  
}

void transfer(Cgicc & cgi)
{

  int fee=5;
  char amount_b[10];
  char iban_b[IBAN_LEN+1];

  if (!is_valid_user(cgi))
    {
      cout<<h2("You need to be logged in to trasfer money");
      return login(cgi);
    }

  vector<field_info> tmp_v;
  tmp_v.push_back(field_info("Amount:","text","amount"));
  tmp_v.push_back(field_info("IBAN:","text","iban"));
  static int sentinel=-1;
  if (data_form(cgi,"transfer",tmp_v,sentinel))
    cout<<p("So you want to put your money back under you matress? That's alright...")<<endl;
  else
    {

      vector<string> tmp_vs;
      tmp_vs.push_back("iban");
      tmp_vs.push_back("amount");
      if (data_present(cgi,tmp_vs))

	{
	  strcpy(amount_b,tmp_vs[1].c_str());
	  //cout<<"AMOUNT: "<<amount_b;

	  int amount_num=0;
	  try
	    {
	      amount_num=boost::lexical_cast<int>(amount_b);
	    }
	  catch(boost::bad_lexical_cast &)
	    {
	      send_header(cgi);
	      error("The amount you submitted is not valid");
	      transfer(cgi);
	      return;
	    }

	  strcpy(iban_b,tmp_vs[0].c_str());
	  int timestamp=time(NULL);
	  string uname,password;
	  get_cookieval(cgi,uname,password);	      
	  int current_amount=get_deposit_value(uname);
	  int transfer_amount=amount_num+fee;

	  if (current_amount> transfer_amount)
	    {
	      fs::ofstream deposit_file((format("%s/%s/%s")%ACCOUNT_DIR%uname%DEPOSIT_FILENAME).str());
	      deposit_file<< current_amount-transfer_amount;
	      deposit_file.close();	      
	      int transaction_file=open((format("%s/%s_%d.txt")%TRANSACTION_DIR%uname%timestamp).str().c_str(), O_CREAT|O_TRUNC|O_WRONLY, S_IRUSR|S_IWUSR);

	      write(transaction_file,amount_b,strlen(amount_b));
	      write(transaction_file," ",1);
	      write(transaction_file,iban_b,IBAN_LEN);
	      close(transaction_file);

	      success((format("Transfer of %d$ completed successfully")%amount_num).str());
	      browse_value(cgi);
	    }
	  else
	    {
	      send_header(cgi);
	      error((format("Invalid trasfer. Total (transfer+%d$ fee) is %d and your balance is %d")%fee%transfer_amount%current_amount).str());
	      transfer(cgi);

	    }
	  
	}
    }
}

void browse_value(Cgicc & cgi)
{
  if (!is_valid_user(cgi))
    {
      cout<<h2("You need to be logged in to browse your value");
      return login(cgi);
    }
  
  time_t timestamp=time(NULL);
  string uname, password;
  get_cookieval(cgi,uname,password);
  int current_amount=get_deposit_value(uname);
  cout<<h3((format("Your current balance is: %s$")%current_amount).str())<<br()<<cgicc::div()<<endl;

  cout<<table()<<tr();
  for(typeof(stocks_map.begin()) i=stocks_map.begin();i!=stocks_map.end();++i)
    cout<<(format("<td><img src=\"../images/%s.jpg\"></td><td> %s: %d$</td>")%i->first%get<2>(i->second)%get_stocks_value(uname,timestamp,i->first)).str()<<endl;
  cout<<tr()<<table()<<cgicc::div()<<endl;
}

string nice_header(string filename,string uname)
{ 
  using namespace boost::posix_time;
  using namespace boost::local_time;
  using namespace boost::gregorian;
  typedef boost::date_time::local_adjustor<ptime, -8, us_dst> us_pacific;
  time_duration d=seconds(boost::lexical_cast<long int>( filename.substr(0,filename.find('_',0)  )));
  ptime now=us_pacific::utc_to_local(ptime(date(1970,1,1))+ d);
  return to_simple_string(now)+" by "+uname;
}

void leave_comment(Cgicc & cgi)
{
  if (!is_valid_user(cgi))
    {
      cout<<h2("You need to be logged in to leave a comment");
      return login(cgi);
    }

  vector<field_info> tmp_v;
  static int sentinel=-1;
  string uname,password;
  if (data_form(cgi,"leave_comment",tmp_v,sentinel,true));
  else
    {
      vector<string> tmp_vs;
      tmp_vs.push_back("comment");
      
      //string uname, password;
      if (data_present(cgi,tmp_vs))
	{
	  string comment=tmp_vs[0];
	  get_cookieval(cgi,uname,password);
	  time_t timestamp=time(NULL);
	  fs::ofstream comment_file((format("%s/%d_%s.txt")%COMMENT_DIR%timestamp%uname).str());
	  comment_file<< sanitize(comment)<<endl;
	  comment_file.close();	      
	}
      
    }  
  fs::directory_iterator end_iter;
  for ( fs::directory_iterator dir_itr( fs::path(COMMENT_DIR.c_str()) );
	dir_itr != end_iter;
	++dir_itr )
    {
      fs::ifstream comment_file(*dir_itr);
      string comment;
      cout<<cgicc::div()<<h3(nice_header(dir_itr->leaf(),uname));
      while(getline(comment_file,comment))
	cout<<comment<<br();
      cout<<cgicc::div()<<endl;
      comment_file.close();	      
    }

}



void convert(Cgicc & cgi)
{
  if (!is_valid_user(cgi))
    {
      cout<<h2("You need to be logged in to leave a comment");
      return login(cgi);
    }


  vector<field_info> tmp_v;
  vector<int> stock_cur_val;
  static int sentinel=-1;

  for(typeof(stocks_map.begin()) i=stocks_map.begin();i!=stocks_map.end();++i)
    tmp_v.push_back(field_info( (format("Amount to move to %s :")%get<2>(i->second)).str() ,"text", i->first));


  if (data_form(cgi,"convert",tmp_v,sentinel))
      cout<<p("Put a positive amount (such as 10) if you want to transfer from your deposit to the stock, a negative value if you want to move money back from stock to your deposit or 0 if you just don't care")<<endl;
  else
    {


      vector<string> tmp_vs;
      for(typeof(stocks_map.begin()) i=stocks_map.begin();i!=stocks_map.end();++i)
	  tmp_vs.push_back(i->first);
      
      //string uname, password;
      if (data_present(cgi,tmp_vs))
	{
	  int timestamp=time(NULL);
	  vector<string>::const_iterator j=tmp_vs.begin();
	  
	  string uname,password;
	  get_cookieval(cgi,uname,password);
	  int tosub=0;
	  for(typeof(stocks_map.begin()) i=stocks_map.begin();i!=stocks_map.end();++i)
	    {	
      
	      if (-boost::lexical_cast<int>(*j) > get_stocks_value(uname,timestamp,i->first))
		{
		  send_header(cgi);
		  error((format("You can't operate the transfer from stock %s")%get<2>(i->second)).str());
		  convert(cgi);
		}
	      else
		tosub+=boost::lexical_cast<int>(*j);
	      ++j;
	    }
	  if (tosub>get_deposit_value(uname))
	    {
	      send_header(cgi);
	      error((format("You can't operate the transfer since the total amount (%d$) is greater than the one you have in the deposit (%d$)")%tosub%get_deposit_value(uname)).str());
	      convert(cgi);
	    }
	  else
	    {
	      j=tmp_vs.begin();
	      get_cookieval(cgi,uname,password);
	      for(typeof(stocks_map.begin()) i=stocks_map.begin();i!=stocks_map.end();++i)
		{	
		  
		  int amount_new=get_stocks_value(uname,timestamp,i->first)+boost::lexical_cast<int>(*j);
		  fs::ofstream stock_file((format("%s/%s/%s.txt")%ACCOUNT_DIR%uname%(i->first)).str());
		  stock_file<< amount_new<<' '<<timestamp;    
		  stock_file.close();	      
		  ++j;
		}
	      int current_amount=get_deposit_value(uname);
	      fs::ofstream deposit_file((format("%s/%s/%s")%ACCOUNT_DIR%uname%DEPOSIT_FILENAME).str());
	      deposit_file<< current_amount-tosub;
	      deposit_file.close();	      

	      success(format("Transfer completed successfully").str());
	      browse_value(cgi);

	    }
	  
	}
      
    }
  
}


int 
main(int argc, 
     char **argv)
{

  
  directory_map["login"]=dir_tuple(login,"Login");
  directory_map["browse_value"]=dir_tuple(browse_value,"Browse you current value");
  directory_map["create_user"]=dir_tuple(create_user,"Create a new user");
  directory_map["deposit"]=dir_tuple(deposit,"Make a deposit");
  directory_map["transfer"]=dir_tuple(transfer,"Take off money from deposit");
  directory_map["leave_comment"]=dir_tuple(leave_comment,"Leave a comment about the service");
  directory_map["convert"]=dir_tuple(convert,"Transfer money from your deposit to stocks");
  directory_map["logout"]=dir_tuple(logout,"Logout");
  

  stocks_map["pipes"]=make_tuple(0,0,"Corncob Pipes");
  stocks_map["banjos"]=make_tuple(1,1,"Banjos");
  stocks_map["moonshine"]=make_tuple(0,0,"XXX Moonshine clay jugs");

  try {
      Cgicc cgi;
      
      form_iterator action = cgi.getElement("action");
      
      if(action != cgi.getElements().end() && directory_map.find(**action)!=directory_map.end())
	{
	  if (**action!="login" && **action!="logout")
	    send_header(cgi);	    
	  get<0>(directory_map[**action])(cgi);

	}
      else
	{
	  send_header(cgi);
	  index_page(cgi);
	}

      cout<<trailer_html<<body() << html();
   }
   catch(exception& e) {
     
   }
}

