#! /bin/bash 

while read line           
do           
    python populate.py "agraph.ini" $line "data/"           
done < perseus_works.txt