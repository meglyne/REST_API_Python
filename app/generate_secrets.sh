#!/bin/sh

# The script accepts one argument, the domain for the certificate
DOMAIN="$1"
if [ -z "$DOMAIN" ]; then
    echo "Usage: $(basename $0) <domain>"
    exit 1
fi

fail_if_error() {
    [ $1 != 0 ] && {
        unset PASSPHRASE
        exit 10
    }
}

#Generate a passphrase
export PASSPHRASE=$(head -c 500 /dev/urandom | tr -dc a-z0-9A-Z | head -c 128; echo)

# Certificate details
# Replace items with your own info
subj="
C=FR
ST=Ile-de-France
O=Blep
localityName=Paris
commonName=$DOMAIN
organizationalUnitName=Blep Blep
emailAddress=admin@example.com
"

# Generate the server private key
openssl genrsa -des3 -out app/instance/$DOMAIN.key -passout env:PASSPHRASE 2048
fail_if_error $?

# Generate the CSR
openssl req \
    -new \
    -batch \
    -subj "$(echo -n "$subj" | tr "\n" "/")" \
    -key app/instance/$DOMAIN.key \
    -out app/instance/$DOMAIN.csr \
    -passin env:PASSPHRASE
fail_if_error $?
cp app/instance/$DOMAIN.key app/instance/$DOMAIN.key.org
fail_if_error $?

#Strip the password so we don't have to type it everytime we restart Flask service
openssl rsa -in app/instance/$DOMAIN.key.org -out app/instance/$DOMAIN.key -passin env:PASSPHRASE
fail_if_error $?

#Generate the certificate (good for 1 year)
openssl x509 -req -days 3650 -in app/instance/$DOMAIN.csr -signkey app/instance/$DOMAIN.key -out app/instance/$DOMAIN.crt
fail_if_error $?
