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

# This is a test program to try out making certificates with Python instead of shell

from OpenSSL import crypto

password = input("Password:")

ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, open("/home/eric/certs/CA.crt", "rb").read())
ca_priv = crypto.load_privatekey(crypto.FILETYPE_PEM, open("/home/eric/certs/CA.key", "rb").read(), bytes(password, "utf8"))

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

cert = crypto.X509()
cert.set_serial_number(19)
cert.set_subject(csrrequest.get_subject())
cert.set_issuer(ca_cert.get_subject())
cert.gmtime_adj_notBefore( 0 )
cert.gmtime_adj_notAfter( 365*24*60*60 )
cert.set_pubkey(csrrequest.get_pubkey())
cert.sign(ca_priv, "sha1")

with open("from_python.crt", "wb") as f:
  f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

#print(str(crypto.dump_certificate(crypto.FILETYPE_PEM, cert)))

p12 = crypto.PKCS12()
p12.set_privatekey(psec)
p12.set_certificate(cert)
p12.set_ca_certificates([ca_cert])
open("container.pfx", "wb").write(p12.export())
