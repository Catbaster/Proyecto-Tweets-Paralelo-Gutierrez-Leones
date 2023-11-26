#starting from root dir after the pull
# the first parameter is the repository name
# the second parameters is the directorry with the input files
# the third parameter is the initial date
# the fourth parameter is the final date

#!/bin/bash

cp -f ht.txt $1
rm -f ${1}.txt

cd $1

sec=$(py generador.py -d ${2} -jrt -jm -jcrt -h ht.txt -fi ${3} -ff ${4})
p2=$(mpiexec -n 2 py generadorp.py -d ${2} -jrt -jm -jcrt -h ht.txt -fi ${3} -ff ${4})
p4=$(mpiexec -n 4 py generadorp.py -d ${2} -jrt -jm -jcrt -h ht.txt -fi ${3} -ff ${4})
p6=$(mpiexec -n 6 py generadorp.py -d ${2} -jrt -jm -jcrt -h ht.txt -fi ${3} -ff ${4})
p8=$(mpiexec -n 8 py generadorp.py -d ${2} -jrt -jm -jcrt -h ht.txt -fi ${3} -ff ${4})


echo $sec $p2 $p4 $p6 $p8$>> ../${1}.txt


cd ..