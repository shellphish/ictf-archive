var ToolBar_Supported = ToolBar_Supported ;
   
if (ToolBar_Supported != null && ToolBar_Supported == true)
{
//To Turn on/off Frame support, set Frame_Supported = true/false.
Frame_Supported = false;

// Customize default ICP menu color - bgColor, fontColor, mouseoverColor
setDefaultICPMenuColor("#0A6CCE", "#FFFFFF", "#cc0000");


// Customize toolbar background color
setToolbarBGColor("#0A6CCE");

// display ICP Banner
setICPBanner("/isapi/gomscom.asp?target=/presspass/images/bnr-microsoft.gif","/","Microsoft.com Home") ;

 // display customer Right side image
	setBanner("/presspass/images/1pxt.gif","","","<!--BEG_MSC_BANNER-->","<!--END_MSC_BANNER-->");

	
//***** Add ICP menus *****
//Home
addICPMenu("HomeMenu", "PressPass Home", "","/isapi/gomscom.asp?target=/presspass/");
	

//PRContacts
addICPMenu("PRContactsMenu", "PR Contacts", "", "/isapi/gomscom.asp?target=/presspass/contactpr.asp");
		

//About Microsoft
addICPMenu("MicrosoftMenu", "Fast Facts About Microsoft", "","/isapi/gomscom.asp?target=/presspass/inside_ms.asp");

//Site Map
addICPMenu("MicrosoftMenu", "Site Map", "","/isapi/gomscom.asp?target=/presspass/sitemap.asp");

}
