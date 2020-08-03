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

# This is a test program to try out making certificates with Python by calling a shell program

from OpenSSL import crypto
import sys
import subprocess


def generate(cn, passphrase=None):
  csrrequest = crypto.X509Req()
  csrrequest.get_subject().C = "US"
  csrrequest.get_subject().O = "eric.willisson.org"
  csrrequest.get_subject().CN = "Eric; Python"

  psec = crypto.PKey()
  psec.generate_key(crypto.TYPE_RSA, 2048)

  with open("from_python.key", "wb") as f:
    f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, psec))

  csrrequest.set_pubkey(psec)
  csrrequest.sign(psec, "sha1")

  with open("from_python.csr", "wb") as f:
    f.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, csrrequest))

  password = input("CA Password:")

  p = subprocess.Popen(["openssl", "x509", "-req", "-days", "365", "-in", "from_python.csr", "-CA", "CA.crt", "-CAkey", "CA.key", "-set_serial", "19", "-out", "from_python.crt", "-passin", "pass:" + password], stderr=subprocess.PIPE)
  p.communicate()

  ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, open("/home/eric/certs/CA.crt", "rb").read())
  cert = crypto.load_certificate(crypto.FILETYPE_PEM, open("from_python.crt", "rb").read())
  
  p12 = crypto.PKCS12()
  p12.set_privatekey(psec)
  p12.set_certificate(cert)
  p12.set_ca_certificates([ca_cert])
  open("user.pfx", "wb").write(p12.export())


def main():
  passphrase = None

  if len(sys.argv) >= 2:
    cn = sys.argv.pop()
  else:
    print("Usage: {} cn [passphrase] [expiration]".format(sys.argv[0]))
    exit()
  if len(sys.argv) >= 2:
    passphrase = sys.argv.pop()
  generate(cn, passphrase)


if __name__ == "__main__":
  main()
