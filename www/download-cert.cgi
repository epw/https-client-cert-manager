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

CERT_DIR = os.path.join("/home/eric", "certs", "generated")

def cert(filename):
  pathname = os.path.join(CERT_DIR, filename)
  if filename.find("/") != -1 or not os.path.exists(pathname):
    print("Content-Type: text/plain\n")
    print("Error: Certificate ID is '{}', which is illegal".format(filename))
    return
  
  sys.stdout.buffer.write(b"Content-Type: application/x-x509-user-cert\r\n\r\n")
  with open(pathname, "rb") as f:
    sys.stdout.buffer.write(f.read())


def main():
  params = cgi.FieldStorage()
  cert(params.getfirst("id"))


if __name__ == "__main__":
  main()
  
