openssl asn1parse -in public.pem
echo
openssl asn1parse -in public.pem -strparse 18
echo
openssl asn1parse -in private.pem
