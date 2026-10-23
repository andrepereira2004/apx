# U.Porto eduroam profile

On 2026-10-06 the actual radius.up.pt server presented a certificate issued by
GEANT TLS ECC 1 under HARICA TLS ECC Root CA 2021, valid from 2026-07-22 to
2027-02-06. The public certificate chain was extracted from EAP TLS in memory;
no identities, passwords or packet captures were saved. OpenSSL verified the
received chain and hostname radius.up.pt against the existing Host system trust.

ca.pem is the Hellenic Academic and Research Institutions ECC RootCA 2015 trust anchor extracted from the Host's
existing /etc/ssl/certs/ca-certificates.crt, not a trust-on-first-use certificate.
Install it as /etc/ssl/certs/apx-uporto-eduroam.pem. This is a profile-specific
trust file and does not modify general system trust.

The official CAT institution 610/profile 6529 still supplied an old Comodo chain
on 2026-10-06, which cannot verify the currently presented certificate. Its
PEAP/MSCHAPV2 settings and radius*.up.pt server names remain consistent with the
observed server. Source: https://cat.eduroam.org/?idp=610
The current APX contract accepts a single mask; *.up.pt retains domain validation.
The UI preset applies only to eduroam @fe.up.pt/@up.pt identities with explicit
up.pt/*.up.pt domains. Actual account authentication requires owner observation.

The server sends a HARICA 2021 certificate cross-signed by the 2015 root. OpenSSL
can use the shorter path to the 2021 system root, but libell/iwd's kernel-backed
verification rejected that full chain against the 2021 root. It passed against
the 2015 root from system trust. Verified with l_certchain_verify using the
received public three-certificate chain on 2026-10-06. This is why the 2015
anchor is configured rather than the 2021 self-signed certificate.
