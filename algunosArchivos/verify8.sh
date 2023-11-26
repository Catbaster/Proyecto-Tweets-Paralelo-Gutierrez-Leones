#starting from root dir after the pull
# the first parameter is the repository name
# the second parameters is the directorry with the input files
# the third parameter is the initial date
# the fourth parameter is the final date

#!/bin/bash

cp -f ht.txt $1
rm -f ${1}.txt

cd $1


p8=$(mpiexec -n 8 py generadorp.py -d ${2} -jrt -jm -jcrt -h ht.txt -fi ${3} -ff ${4})


echo  $p8 $>> ../${1}.txt


cd ..