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

# Variant of generate.cgi that assigns a random name and so anyone can use it.

import cgi, cgitb
cgitb.enable()

from datetime import datetime
import dateutil.parser
import hashlib
import math
from OpenSSL import crypto
import os
import pytz
import random
from types import SimpleNamespace
from urllib.parse import urlencode

try:
  import priv
except ModuleNotFoundError:
  priv = SimpleNamespace(password="")


CA_DIR = "/home/eric/certs"
CERT_DIR = os.path.join("/home/eric", "certs", "generated")

PUBLIC_DOWNLOAD = "https://eric.willisson.org/download-cert.cgi?id={filename}&type={type}"

def cert_file(filename):
  return os.path.join(CA_DIR, filename)


def next_serial_number():
  with open(cert_file("CA.conf")) as f:
    sn = int(f.readline().split("next_serial ")[1])
  with open(cert_file("CA.conf"), "w") as f:
    f.write("next_serial {}".format(sn+1))
  return sn


def utcnow():
  return datetime.now(tz=pytz.utc)


def process_expiration(expiration):
  if expiration is None:
    return 365*24*60*60
  return max(0, int((pytz.timezone("America/New_York").localize(dateutil.parser.parse(expiration)) - utcnow()).total_seconds()))


def random_letter():
  return chr(97 + math.floor(random.random()*26))

def random_name():
  return "".join([random_letter() for _ in range(10)])


def cryptography(cn, passphrase, expiration=None):
  ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(cert_file("CA.crt"), "rb").read())
  ca_priv = crypto.load_privatekey(crypto.FILETYPE_PEM, open(cert_file("CA.key"), "rb").read(), bytes(priv.password, "utf8"))

  csrrequest = crypto.X509Req()
  csrrequest.get_subject().C = "US"
  csrrequest.get_subject().O = "eric.willisson.org"
  csrrequest.get_subject().CN = cn

  psec = crypto.PKey()
  psec.generate_key(crypto.TYPE_RSA, 2048)

  csrrequest.set_pubkey(psec)
  csrrequest.sign(psec, "sha256")

  serial_number = next_serial_number()
  
  cert = crypto.X509()
  cert.set_serial_number(serial_number)
  cert.set_subject(csrrequest.get_subject())
  cert.set_issuer(ca_cert.get_subject())
  cert.gmtime_adj_notBefore( 0 )
  cert.gmtime_adj_notAfter( process_expiration(expiration) )
  cert.set_pubkey(csrrequest.get_pubkey())
  cert.sign(ca_priv, "sha256")

  buf = []
  for _ in range(16):
    buf.append(chr(random.randint(0, 128)))
  filename = hashlib.sha256(bytes(datetime.isoformat(datetime.now()) + "".join(buf), "utf8")).hexdigest() + ".pfx"
  p12 = crypto.PKCS12()
  p12.set_privatekey(psec)
  p12.set_certificate(cert)
  p12.set_ca_certificates([ca_cert])

  open(os.path.join(CERT_DIR, filename), "wb").write(p12.export(passphrase=passphrase))
    
  return filename


def generate(suffix, passphrase=None, expiration=None):
  print("Content-Type: text/html\n")

  cn = name = random_name()
  new_cn = name
  if suffix:
    new_cn += "; " + suffix
  if passphrase == "":
    passphrase = None
  filename = cryptography(new_cn, passphrase, expiration)

  with open("generate.template.html") as f:
    print(f.read().format(cn=cn, new_cn=new_cn, extra_css="#another { display: none; }",
                          crt_link=PUBLIC_DOWNLOAD.format(filename=filename, type="crt"),
                          pfx_link=PUBLIC_DOWNLOAD.format(filename=filename, type="pfx"),
                          explain_link=PUBLIC_DOWNLOAD.format(filename=filename, type="explain") + "&" + urlencode({"cn": new_cn, "oldcn": cn})))


def main():
  params = cgi.FieldStorage()
  generate(params.getfirst("suffix"),
           params.getfirst("passphrase", None), params.getfirst("expiration", None))
  

if __name__ == "__main__":
  main()
  
