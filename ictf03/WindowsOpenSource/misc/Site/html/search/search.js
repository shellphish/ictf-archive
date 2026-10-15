window.onload = Init;

// Set focus if appropriate, bind onclick event to all relevant anchors.
function Init()
{
	// If on search page, set focus to first text box.
	if(document.location.pathname.toLowerCase().indexOf("search.aspx") > -1) document.frmS.qu.focus();

	// Get container of our content
//	var oContentDiv = document.getElementById("divContent");
//	if(oContentDiv != null)
//	{
//		// Get all links under it
//		var oLinks = oContentDiv.getElementsByTagName("a");
//		if(oLinks != null)
//		{
//			// Bind onclick to links
//			var iLinksCount = oLinks.length;
//			for(var i=0; i<iLinksCount; i++){ oLinks[i].onclick = ProcessLink; }
//		}
//	}
}

function ProcessLink(e)
{
	var sAgent = navigator.userAgent.toLowerCase(); 
	var bIsIE = (sAgent.indexOf("msie") > -1);		// If IE, and Appversion 4, it is IE 5+
	var bIsNetscape = (sAgent.indexOf("gecko") > -1);// This catches all gecko engines

	// Get clicked element
	var elem;
	if(true == bIsIE) elem = event.srcElement;
	else elem = e.target.parentNode;

	// If not an anchor, iterate up till you find one - exit if hit the body tag.
	while (elem.tagName != "A")
	{
		if (elem.tagName == "BODY") return;
		if (bIsIE) elem = elem.parentElement;
		else if (bIsNetscape) elem = elem.parentNode;
	}

	// Get number of the result clicked, if any
	var oResultNumber = null;
	var iResultNumber = 0;
	oResultNumber = elem.attributes["n"];
	if(typeof(oResultNumber) != 'undefined') iResultNumber = oResultNumber.value;

	// Get category of target, if any
	var oCat = null;
	var iCat = 0;
	oCat = elem.attributes["c"];
	if(typeof(oCat) != 'undefined') iCat = oCat.value;

	// Get navAction
	var oNA = null;
	var iNA = "";
	var oNA = elem.attributes["na"];
	if(typeof(oNA) != 'undefined') iNA = oNA.value;

	// Page to be directed to
	var infoUrl = "info.aspx";

	// Tweak existing querystring to add to target url.
	var qp = document.location.search;
	if (qp.indexOf("?") == 0) qp = qp.substring(1);
	if (qp.length > 0) qp = "&" + qp;

	// Finish url
	var sTarget = elem.href;

    //For intra-page links on the pages in the current domain, no need to report stats. 
    if(sTarget.toLowerCase().indexOf("#") > -1)
    {
        if(sTarget.toLowerCase().indexOf(document.location.hostname + document.location.pathname) > -1) return;
    }

	// Try using encodeURIComponent - if not supported (like ie5.0), should fall to catch block and use escape instead.
	// Try/catch is not supported in some downlevel - but this script isn't served to them
	try{infoUrl += "?u=" + encodeURIComponent(sTarget) + "&n=" + encodeURIComponent(iResultNumber) + "&na=" + encodeURIComponent(iNA) + "&c=" + encodeURIComponent(iCat) + qp;}
	catch(e){infoUrl += "?u=" + escape(sTarget) + "&n=" + escape(iResultNumber) + "&na=" + escape(iNA) + "&c=" + escape(iCat) + qp;}
	
	// Do redirect. Sometimes with slow browser reaction and rapid clicks this can get called more than once.
	// Ensure no repetition-check if existing href already modified
	if (elem.href.toString().indexOf("info.aspx") != 0) elem.href = infoUrl;
}
