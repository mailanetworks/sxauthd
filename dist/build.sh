#!/usr/bin/bash
# Load support functions
. ../../lib/functions.sh

PROG=cyrus-sasl      # App name
VER=2.1.26            # App version
VERHUMAN=$VER   # Human-readable version
#PVER=          # Branch (set in config.sh, override here if needed)
PKG=sxaos/daemon/saslauthd            # Package name (e.g. library/foo)
SUMMARY="Cyrus SASL"      # One-liner, must be filled in
DESC="$SUMMARY"         # Longer description, must be filled in

BUILD_DEPENDS_IPS="library/security/openssl naming/ldap"
RUN_DEPENDS_IPS="$BUILD_DEPENDS_IPS"

BUILDARCH=64
CONFIGURE_OPTS="--disable-gssapi --includedir=/usr/include/sasl2"

init
download_source $PROG $PROG $VER
patch_source
prep_build

build
make_isa_stub
make_package
clean_up

# Vim hints
# vim:ts=4:sw=4:et:
