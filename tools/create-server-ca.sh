#! /bin/bash

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



# Based on https://manintheit.org/security/ssl-client-certificate-authentication-with-apache/

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <ca.key>"
    echo "  note: also generates <ca.crt> and <ca.conf>"
    exit 1
fi

CA=`basename "$1" .key`; shift
CA_KEY="$CA.key"
CA_CRT="$CA.crt"
CA_CONF="$CA.conf"

echo "Creating new CA certificate, which will be used to sign client certs."
echo "It will last for 365 days. The passphrase will be used when signing client certs."
echo

openssl genrsa -des3 -out "$CA_KEY" 4096 || exit 1

echo
echo "You are being prompted for the passphrase again because a second command is running."

openssl req -new -x509 -days 365 -key "$CA_KEY" -out "$CA_CRT" || exit 1

echo "next_serial 01" > "$CA_CONF"
