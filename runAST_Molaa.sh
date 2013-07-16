#!/bin/bash

## get pin numbers from code
numbers=$(grep "PINS =\|PINS=" ast_molaa.py | sed 's/[^0-9,]//g' | sed 's/,/ /g')

## do the export thing
for n in ${numbers} 
do
   gpio export ${n} out
done

# start AST
python ast_molaa.py --inport 8989 --localnetport 8888 --localnet 127.0.0.1
