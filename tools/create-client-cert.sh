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

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <client.pfx> <ca.key> [name]"
    echo "  note: also requires <ca.crt> and <ca.conf>"
    exit 1
fi

CLIENT=`basename "$1" .pfx`; shift
CA=`basename "$1" .key`; shift

if [[ $# -gt 0 ]]; then
    export CN=$1; shift
else
    CN=
fi

CLIENT_KEY="$CLIENT.key"
CLIENT_CSR="$CLIENT.csr"
CLIENT_CRT="$CLIENT.crt"
CLIENT_PFX="$CLIENT.pfx"

CA_KEY="$CA.key"
CA_CRT="$CA.crt"
CA_CONF="$CA.conf"

SERIAL=`grep next_serial "$CA_CONF" | awk '{print $2}'`

if [[ -z "$SERIAL" ]]; then
    echo "Error reading next serial number from $CA_CONF"
    exit 1
fi

CMD="openssl req -newkey rsa:2048 -nodes -keyout $CLIENT_KEY -out $CLIENT_CSR"
if [[ -n "$CN" ]]; then
    $CMD -subj "/C=US/O=eric.willisson.org/CN=$CN"
else
    echo "Use the Common Name field below for primary identification."
    $CMD
fi

openssl x509 -req -days 365 -in "$CLIENT_CSR" -CA "$CA_CRT" -CAkey "$CA_KEY" -set_serial "$SERIAL" -out "$CLIENT_CRT" || exit 1
openssl pkcs12 -export -out "$CLIENT_PFX" -inkey "$CLIENT_KEY" -in "$CLIENT_CRT" -certfile "$CA_CRT"

NEXT_SERIAL=$(printf "%02d" `expr $SERIAL + 1`)

sed -i "s/next_serial .*$/next_serial $NEXT_SERIAL/" $CA_CONF

echo "Now, you can securely send $CLIENT_PFX to your clients and install them."
echo "On Android, selecting the file will usually invoke a Certificate Installer."
echo "On Chrome, you have to go to Settings -> Privacy and security -> (more) -> Manage certificates"

rm "$CLIENT_KEY"
rm "$CLIENT_CSR"
rm "$CLIENT_CRT"
