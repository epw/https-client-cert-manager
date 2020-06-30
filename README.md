# HTTPS Client Cert Manager

This is not an officially supported Google product.

This has not yet been implemented, but here is the plan:

This facilitates generating client certificates for a Web server, which can be
installed on individual Web clients and then used for authentication. This is a
technology that has existed for many years but is not widely used (perhaps
outside of some corporate settings). It will include a program that generates a
certificate authority (CA) for the server, and a program to generate new client
certificates from that CA. It will also include guidance on how to require a
client certificate for a Web page, and tools for identifying users by their
client certificates. Finally, it will have a Web page which can be included on a
server that can generate a new client certificate for a holder of an old one.
