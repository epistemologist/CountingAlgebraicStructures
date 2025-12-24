#!/bin/bash

set -ex
if [ ! -f ./LADR-2009-11A.tar.gz ]; then
	wget https://www.cs.unm.edu/~mccune/prover9/download/LADR-2009-11A.tar.gz 
fi
tar xvzf LADR-2009-11A.tar.gz
(
	cd LADR-2009-11A/ &&
	find . -name 'Makefile' -exec sed -i '/^[[:space:]]*\$(CC)/ s/$/ -lm/' {} + &&
	find . -name 'Makefile' -exec sed -i 's/-Wall/-Wall -fpermissive/g' {} + &&
	make all
)
# rm LADR-2009-11A.tar.gz

