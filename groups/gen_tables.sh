#!/bin/bash
set -ex
LADR_LOCATION="../LADR-2009-11A"

order=$1;
outfile=$2;
tmpfile=$(mktemp)
echo "
assign(domain_size, $order).
assign(max_models, -1).
set(verbose).
formulas(theory).
    % Associativity
    (x*y)*z = x*(y*z).
    % Identity element
    e*x=x.
    % Inverses
    x'*x=e.
end_of_list.
" | tail -c +2 | stdbuf -oL $LADR_LOCATION/bin/mace4 | tee $tmpfile ;
cat $tmpfile | $LADR_LOCATION/bin/interpformat portable > $outfile;
rm $tmpfile;
