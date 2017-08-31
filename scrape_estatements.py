from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date
import logging
import re
import requests
import sys
import os
import errno
from time import sleep

logging.basicConfig(level=logging.INFO)

# assume you fetched this already
file_name = "main.html"

class Statement(object):
    # SID=[29BA-25CE348-0BED85]&STMID=202022409
    parse_ids_pattern = re.compile(r'SID=\[(\S+?)]&STMID=(\d+)')

    def __init__(self,  account, link, desc, date):
        self.log = logging.getLogger("statement")

        parsed_date = parse_date(date)
        self.date = parsed_date.strftime("%Y-%m-%d")
        self.desc = desc

        self.account = account

        matches = re.search(self.parse_ids_pattern, link)
        if (matches):
            log.info("match")
            self.sid = matches.groups(0)[0] 
            self.stmt_id =  matches.groups(0)[1]
            self.log = logging.getLogger("statement.%s" % (self.stmt_id))
        else:
            log.error(link)
            raise(Exception("sdfsd"))


    def __repr__(self):
        return "SID: %s, STMT_ID: %s, DATE: %s, Account: %s %s" % (self.sid, self.stmt_id, self.date, self.account, self.desc)
    def __str__(self):
        return "SID: %s, STMT_ID: %s, DATE: %s, Account: %s %s" % (self.sid, self.stmt_id, self.date, self.account, self.desc)

    def request_generate_pdf(self):
        """
        There is an unusual workflow where we first request that a PDF be
        generated.  We name it by session ID and statement ID.  The response is
        expected to be a redirect to a "waiting" page.   There is some polling
        operation, that would then separately make a request to fetch the PDF.
        """
        urlfmt = "https://estatements.centrue.com/rpweb.dll/GETPDF?SID=[%s]&STMID=%s"
        url = urlfmt % (self.sid, self.stmt_id)
        self.log.info("Fetcing url: %s", url)
        r = requests.get(url, allow_redirects=False)
        if (r.status_code == 302 and 'WAIT' in r.headers['Location']):
            self.log.info("Generate success")
        else:
            raise(Exception("error"))


    def download_pdf(self):
        self.request_generate_pdf()
	sleep(5)
        urlfmt = "https://estatements.centrue.com/rpweb.dll/SHOWPDF?SID=[%s]"
        url = urlfmt % (self.sid)
        self.log.info("Fetching url: %s", url)

        r = requests.get(url, allow_redirects=False)
        if (r.status_code == 200 and 'pdf' in r.headers['Content-Type']):
            self.log.info("Download success")
        else:
            raise(Exception("error"))

        self.log.info("Saving to %s", self.save_path())
	with open(self.save_path(), 'wb') as pdf:
	    pdf.write(r.content)
		


    def save_path(self):
        """
        Folder structure will be 

            document type\
                Account number\
                    Date.pdf
                    ...

        Creates dirs as needed.  Returns path/filename relative to working dir.

        """
        desc_string = self.desc.replace(" ", "_")
        path = os.path.join(desc_string, self.account)

	self.log.info("creating path %s", path)
	try:
	    os.makedirs(path)
	except OSError as exc: 
	    if exc.errno == errno.EEXIST and os.path.isdir(path):
		pass
	    else:
		raise
        file_name = os.path.join(path, "%s.pdf" % (self.date))
        return file_name


        



log = logging.getLogger("main")
with open(file_name) as fp:
    soup = BeautifulSoup(fp, "html.parser" )

statements_table = soup.find_all("table")[2]
rows = statements_table.find_all("tr")

statements = []

for row in rows:
    cols = row.find_all("td")
    if not cols:
        continue
    links = row.find_all("a")

    desc = links[2].contents[0]
    date = links[3].contents[0]
    link = links[3]['href']
    account = links[0].contents[0]

    s = Statement(account, link, desc, date)
    statements.append(s)

log.info("Found %s statements", len(statements))
log.info("Downloading statements...")
for s in statements:
    log.info(str(s))
    s.download_pdf()



