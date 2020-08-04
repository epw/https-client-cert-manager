#! /usr/bin/env python3

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cgi, cgitb
cgitb.enable()

import os
import sys
from urllib.parse import parse_qs, urlencode

CERT_DIR = os.path.join("/home/eric", "certs", "generated")

EXTRA_CSS = """
#another { display: none; }
"""

def cert(filename, filetype, cn, oldcn):
  pathname = os.path.join(CERT_DIR, filename)
  if filename.find("/") != -1 or not os.path.exists(pathname):
    print("Content-Type: text/plain\n")
    print("Error: Certificate ID is '{}', which is illegal".format(filename))
    return

  out = sys.stdout.buffer.write
  if filetype == "pfx":
    out(b"Content-Type: application/x-pkcs12\n")
    out(b"Content-Disposition: attachment; filename=user.pfx\n\n")
  elif filetype == "crt":
    out(b"Content-Type: application/x-x509-user-cert\n\n")
  elif filetype == "explain":
    print("Content-Type: text/html\n")
    qs = parse_qs(os.getenv("QUERY_STRING"))
    explain_link = "https://{server_name}{path}?{qs}".format(
      server_name=os.getenv("SERVER_NAME"),
      path=os.getenv("SCRIPT_NAME"),
      qs=urlencode(qs, doseq=True))
    del qs["cn"]
    del qs["oldcn"]
    qs["type"] = "crt"
    crt_link = "?" + urlencode(qs, doseq=True)
    qs["type"] = "pfx"
    pfx_link = "?" + urlencode(qs, doseq=True)
    with open("generate.template.html") as f:
      print(f.read().format(cn=oldcn, new_cn=cn, extra_css=EXTRA_CSS,
                            crt_link=crt_link, pfx_link=pfx_link,
                            explain_link=explain_link))
      return
  else:
    out(b"Content-Type: application/octet-stream\n\n")
  with open(pathname, "rb") as f:
    out(f.read())


def main():
  params = cgi.FieldStorage()
  cert(params.getfirst("id"), params.getfirst("type"), params.getfirst("cn"), params.getfirst("oldcn", "Unknown"))


if __name__ == "__main__":
  main()
  
