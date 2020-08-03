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

from datetime import datetime
import dateutil.parser
import hashlib
from OpenSSL import crypto
import os
import pytz
import random
import subprocess
from types import SimpleNamespace
import util

try:
  import priv
except ModuleNotFoundError:
  priv = SimpleNamespace(password="")


CA_DIR = "/home/eric/certs"
CERT_DIR = os.path.join("/home/eric", "certs", "generated")

# The OpenSSL libraries available in Python don't seem to work with Android.
# In particular, Android can't handle the password-based encryption (PBE)
# mode that Python uses. So, until this is fixed, we have to use the openssl
# shell command instead (with NATIVE_OPENSSL = False)
# Python uses pbeWithSHA1And3-KeyTripleDES-CBC, while the openssl command
# defaults to pbeWithSHA1And40BitRC2-CBC
NATIVE_OPENSSL = False

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


def cryptography(cn, passphrase, expiration=None):
  ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(cert_file("CA.crt"), "rb").read())
  ca_priv = crypto.load_privatekey(crypto.FILETYPE_PEM, open(cert_file("CA.key"), "rb").read(), priv.password)

  csrrequest = crypto.X509Req()
  csrrequest.get_subject().C = "US"
  csrrequest.get_subject().O = "eric.willisson.org"
  csrrequest.get_subject().CN = cn

  psec = crypto.PKey()
  psec.generate_key(crypto.TYPE_RSA, 2048)

  csrrequest.set_pubkey(psec)
  csrrequest.sign(psec, "sha256")

  if NATIVE_OPENSSL:
    cert = crypto.X509()
    cert.set_serial_number(next_serial_number())
    cert.set_subject(csrrequest.get_subject())
    cert.set_issuer(ca_cert.get_subject())
    cert.gmtime_adj_notBefore( 0 )
    cert.gmtime_adj_notAfter( process_expiration(expiration) )
    cert.set_pubkey(csrrequest.get_pubkey())
    cert.sign(ca_priv, "sha256")
  else:
    p = subprocess.Popen(["openssl", "x509", "-req", "-in", "from_python.csr", "-CA", "CA.crt", "-CAkey", "CA.key", "-set_serial", "19", "-out", "from_python.crt", "-passin", "pass:" + priv.password], stderr=subprocess.PIPE)
    p.communicate()
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, open("from_python.crt", "rb").read())

  p12 = crypto.PKCS12()
  p12.set_privatekey(psec)
  p12.set_certificate(cert)
  p12.set_ca_certificates([ca_cert])

  buf = []
  for _ in range(16):
    buf.append(chr(random.randint(0, 128)))
  filename = hashlib.sha256(bytes(datetime.isoformat(datetime.now()) + "".join(buf), "utf8")).hexdigest()
  open(os.path.join(CERT_DIR, filename), "wb").write(p12.export(passphrase=passphrase))
  return filename


def generate(cn, suffix, prefix, passphrase=None, expiration=None):
  print("Content-Type: text/html\n")
  if not util.verify_cert():
    return

  name, _ = util.parse_cn(cn)
  if util.is_admin(name) and prefix:
    new_cn = prefix
  else:
    new_cn = name
  if suffix:
    new_cn += "; " + suffix
  if passphrase == "":
    passphrase = None
  filename = cryptography(new_cn, passphrase, expiration)

  with open("generate.template.html") as f:
    print(f.read().format(cn=cn, new_cn=new_cn, filename=filename))


def main():
  params = cgi.FieldStorage()
  generate(os.getenv("SSL_CLIENT_S_DN_CN"), params.getfirst("suffix"), params.getfirst("prefix"),
           params.getfirst("passphrase", None), params.getfirst("expiration", None))
  

if __name__ == "__main__":
  main()
  
