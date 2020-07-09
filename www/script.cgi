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

import os

import cgi, cgitb
cgitb.enable()


def page():
  print("Content-Type: text/plain\n")
  print("SSL_CLIENT_VERIFY: {}".format(os.getenv("SSL_CLIENT_VERIFY")))
  print()
  for v in os.environ:
    print("{}: {}".format(v, os.getenv(v)))


def main():
  page()
  

if __name__ == "__main__":
  main()
  
