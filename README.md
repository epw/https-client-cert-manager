# HTTPS Client Cert Manager

This is not an officially supported Google product.

## Overview

This project aims to make it easier to use HTTPS Client Certificate
Authentication, which can allow a login system which is more like SSH
keys instead of usernames with passwords.

It requires a Web server using HTTPS, where you can run programs. It
should work with most Web clients. It normally applies to a single
domain name or subdomain, in the same way HTTPS does.

## Usage

First, you'll need to have your server configured to use
HTTPS. Implementing that is beyond the scope of this README, but
[Let's Encrypt](https://letsencrypt.org/) might help.

Then, run `tools/create-server-ca.sh` to create a Certificate
Authority (CA) file for your server. This will create a private
key. Keep this safe, because if you are using this system to
authenticate users, then if someone gets a copy of this private key
they'll be able to make new users and forge identities. Even if you
don't put passphrases on client certificates, it's a good idea to
passphrase-protect this CA.

Configure your Web server to use your CA for client
authentication. (TODO: Expand on this)

Create your first client certificate by running
`tools/create-client-cert.sh` . This will generate a .pfx
file. Install that file in your Web client (TODO: Write a separate
section on this).

Now, a user can use the pages and scripts in `www/` to generate new
certificates. The model this implements is that you must have a
certificate in order to use anything under `www/` . (This must be
configured in the server). You generate a new certificate when you
want to be able to log in from a new client, and then copy it over to
that client.

This system uses the convention that the Common Name (CN) in the
certificate starts with the the user identity, followed by a
semicolon. Thus, it keeps the string before the semicolon constant
while allowing the rest to change when a user (identified by a
certificate, and so having a particular CN) makes a new one. This
allows me, for example, to have "Eric; Desktop" and from it generate
"Eric; Laptop" and "Eric; Phone". It also lets pages on the server
look at the first name for further authentication, such as treating
certificates with the identity "Eric" as admins. As long as you don't
give a certificate with an admin name to anyone else, or generate one
from the CA using `tools/create-client-cert.sh` with a name you mean
to keep controlled, this should be safe for identities.

### Limitations

This system currently has no way for a new, unknown user to create an
account. So, this is not suitable for authentication on a website that
is meant to be used by the public. A publicly-accessible page could
be written that woulld generate new certificates, if desired.

There is no way for the server to recover a user's account, as
written.

## Background

This section needs to be greatly expanded.

In brief, it is possible, using Web standards, to have a Certificate
Authority created for a Web server which can then sign new keypairs
which users can load into their Web clients.

## Future

The biggest issue right now is that distributing new keys is
hard. Ideally, when a user wishes to start to use the site from a new
device, they could log in from an old device, generate a new key, and
send it to the new device, but sending it is still limited to standard
file-transfer methods, for the moment.
