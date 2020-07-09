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
import util

def additional_controls(admin, prefix):
  if not admin:
    return ""
  return """<div class="admin"><label>(Admin only) Use this prefix instead of <code>{prefix}</code>: <input name="prefix"></label></div>""".format(prefix=prefix)

def page(cn):
  print("Content-Type: text/html\n")
  if not util.verify_cert():
    return

  name, suffix = util.parse_cn(cn)

  with open("index.template.html") as f:
    print(f.read().format(cn=cn, name=name, suffix=suffix, additional_controls=additional_controls(util.is_admin(name), name)))


def main():
  page(os.getenv("SSL_CLIENT_S_DN_CN"))
  

if __name__ == "__main__":
  main()
  
