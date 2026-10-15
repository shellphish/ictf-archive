<script language="JavaScript" type="text/javascript">
<!--
var reg = /^[a-zA-z0-9\-\s=@\.]+$/
function isacceptable(field)
{
  if (reg.exec(field)) { return true; }
  return false;
}

function checkregistration(form) 
{
  if (!isacceptable(registration.first.value)) {
    alert( "You are entering a null value or invalid characters in the First Name field!" );
    return false ;
  }
  if (!isacceptable(registration.last.value)) {
    alert( "You are entering a null value or invalid characters in the Last Name field!" );
    return false ;
  }
  if (!isacceptable(registration.dob.value)) {
    alert( "You are entering a null value or invalid characters in the DOB field!" );
    return false ;
  }
  if (!isacceptable(registration.wwid.value)) {
    alert( "You are entering a null value or invalid characters in the World-Wide ID field!" );
    return false ;
  }
  if (!isacceptable(registration.email.value)) {
    alert( "You are entering a null value or invalid characters in the E-mail field!" );
    return false ;
  }
  if (!isacceptable(registration.password.value)) {
    alert( "You are entering a null value or invalid characters in the Password field!" );
    return false ;
  }
  
  return true ;
}

function checkreview(form)
{
  if (!isacceptable(review.wwid.value)) {
    alert( "You are entering a null value or invalid characters in the World-Wide ID field!" );
    return false ;
  }
  if (!isacceptable(review.password.value)) {
    alert( "You are entering a null value or invalid characters in the password field!" );
    return false ;
  }
  
  return true ;
}

function checkupdate(form)
{
  if (!isacceptable(update.first.value)) {
    alert( "You are entering a null value or invalid characters in the First Name field!" );
    return false ;
  }
  if (!isacceptable(update.last.value)) {
    alert( "You are entering a null value or invalid characters in the Last Name field!" );
    return false ;
  }
  if (!isacceptable(update.dob.value)) {
    alert( "You are entering a null value or invalid characters in the DOB field!" );
    return false ;
  }
  if (!isacceptable(update.wwid.value)) {
    alert( "You are entering a null value or invalid characters in the World-Wide ID field!" );
    return false ;
  }
  if (!isacceptable(update.email.value)) {
    alert( "You are entering a null value or invalid characters in the E-mail field!" );
    return false ;
  }
  if (!isacceptable(update.password.value)) {
    alert( "You are entering a null value or invalid characters in the Password field!" );
    return false ;
  }
  if (!isacceptable(update.newfirst.value)) {
    alert( "You are entering a null value or invalid characters in the First Name field!" );
    return false ;
  }
  if (!isacceptable(update.newlast.value)) {
    alert( "You are entering a null value or invalid characters in the Last Name field!" );
    return false ;
  }
  if (!isacceptable(update.newdob.value)) {
    alert( "You are entering a null value or invalid characters in the DOB field!" );
    return false ;
  }
  if (!isacceptable(update.newwwid.value)) {
    alert( "You are entering a null value or invalid characters in the World-Wide ID field!" );
    return false ;
  }
  if (!isacceptable(update.newemail.value)) {
    alert( "You are entering a null value or invalid characters in the E-mail field!" );
    return false ;
  }
  if (!isacceptable(update.newpassword.value)) {
    alert( "You are entering a null value or invalid characters in the Password field!" );
    return false ;
  }
  
  return true ;
}

//-->
</script>
