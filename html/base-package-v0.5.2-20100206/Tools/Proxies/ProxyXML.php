<?php
/*  PROXY SAMPLE CODE - ©2008-2010 Chris Apers / WebApp.Net
    -------------------------------------------------------
    This file is part of the WebApp.Net micro-framework. Any use of this file
    may require to keep the copyright according to the licence provided
    with the framework.

    This code supposed that the external resource will return a valid XML
    response based on the WebApp.Net Data Type Definition. You may change
    this code to transform any other form of XML response.
 */

header("Content-Type: text/xml");

/*  WebApp.Net will send the requested URL to the proxy script with
    the __url query string parameter.
 */
if ($url = $_GET['__url']) {

    /* Fix the URL if needed */
    if (strpos('&amp;', $url) !== FALSE)
        $url = str_replace('&amp;', '&', $url);

    /*    Process the request using cURL API. */
    if ($curl = curl_init($url)) {
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($curl, CURLOPT_USERAGENT, $_SERVER['HTTP_USER_AGENT']);
        $xml = curl_exec($curl);

        /* Return the content and quit. */
        exit($xml);
    }
}

/*    If there is no valid content, we send a default XML content.
 */
echo '<root/>';
?>