Scraping Centrue bank *estatements* web UI
---------------------------------------------

As of 8/2017, Centrue bank is being acquired by Midland states bank.  All the
online statements and account histories will be lost.  The UI for statement
downloads is terrible, of course.  Several clicks in the browser are needed to
view a statement, and then one must manually save the file, choose a filename,
etc.

This tool aims to parse the table of statements on the main page, fetch each
PDF and neatly organize them on the local disk by document type and account
number.


Assumes that the user has manually logged into the estatements interface, and
has fetched the main page by way of wget using the session id SID from the
authenticated session.

    wget 'https://estatements.centrue.com/rpweb.dll/Main?SID=[29BA-25CE348-0BED85]'

It seems that only the time-limited session ID is used to secure any of this
data.

