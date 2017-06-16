#!/bin/bash

BASE_PATH=$(pwd)
VIRTUOSO=7.2.4

apt-get install libssl-dev -q
apt-get install autoconf automake bison flex gawk gperf libtool -q

#git clone git://github.com/openlink/virtuoso-opensource.git
#cd virtuoso-opensource
#git pull origin stable/7
wget --no-check-certificate -q https://github.com/openlink/virtuoso-opensource/archive/v$VIRTUOSO.zip -O virtuoso-opensource.zip

unzip -q virtuoso-opensource.zip
mv virtuoso-opensource-$VIRTUOSO virtuoso-opensource

cd virtuoso-opensource
./autogen.sh

# --disable-all-vads: This parameter disables building all the VAD packages (tutorials, demos, etc.).
# --with-readline: This parameter is used so that the system Readline library is used
# --program-transform-name: Both Virtuoso and unixODBC install a program named isql. Use this parameter to rename virtuosos program to isql-v

./configure --program-transform-name="s/isql/isql-v/" --with-readline --disable-all-vads |& tee #configure.log

# Only output error and warnings
make > /dev/null

# Build tree to start the automated test suite
# make check

make install

## For Virtuoso
#export PATH=$PATH:/usr/local/virtuoso-opensource/bin

/usr/local/virtuoso-opensource/bin/virtuoso-t -f -c /usr/local/virtuoso-opensource/var/lib/virtuoso/db/virtuoso.ini &
#sudo /usr/local/virtuoso-opensource/bin/virtuoso-t -f &

sleep 10

$BASE_PATH/scripts/virtuoso/virtuoso-run-script.sh $BASE_PATH/scripts/virtuoso/load_data.sql