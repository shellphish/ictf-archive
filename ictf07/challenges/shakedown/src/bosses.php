<?php
Header( "HTTP/1.1 301 Moved Permanently" );
Header( "Location: http://" . $_SERVER["SERVER_NAME"] . ":4242/bosses/login/" );
?> 
