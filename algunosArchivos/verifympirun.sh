#starting from root dir after the pull
# the first parameter is the repository name
# the second parameters is the directorry with the input files
# the third parameter is the initial date
# the fourth parameter is the final date

#!/bin/bash

cp -f ht.txt $1
rm -f ${1}.txt

cd $1

sec=$(python3 generador.py -d ${2} -jrt -jm -jcrt -h ht.txt -fi ${3} -ff ${4})
p2=$(mpirun -n 2 -oversubscribe --allow-run-as-root python3 generadorp.py -d ${2} -jrt -jm -jcrt -h ht.txt -fi ${3} -ff ${4})
p4=$(mpirun -n 4 -oversubscribe --allow-run-as-root python3 generadorp.py -d ${2} -jrt -jm -jcrt -h ht.txt -fi ${3} -ff ${4})
p6=$(mpirun -n 6 -oversubscribe --allow-run-as-root python3 generadorp.py -d ${2} -jrt -jm -jcrt -h ht.txt -fi ${3} -ff ${4})
p8=$(mpirun -n 8 -oversubscribe --allow-run-as-root python3 generadorp.py -d ${2} -jrt -jm -jcrt -h ht.txt -fi ${3} -ff ${4})


echo $sec $p2 $p4 $p6 $p8$>> ../${1}.txt


cd ..