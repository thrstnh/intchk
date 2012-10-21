intchk
======

integrity check for data tombs

git clone https://github.com/thrstnh/intchk.git
cd intchk
sudo python setup install

that's it!
Now run "intchk" for the first time and define your stores
in ~/.intchk/config


# help
intchk -h
# rescan all stores
intchk -r
# show log
intchk -l
# show store
intchk -s storename
# rescan one store
intchk -S storename
# dump all data
intchk -d
