# inert analysis fixture
p0 := 'dj0zfGxhbmd1YWdlPWp1c3R8'
p1 := 'cm9sZT1sYXVuY2hlcnx2ZXJk'
p2 := 'aWN0PXN1c3BpY2lvdXN8YXR0'
p3 := 'YWNrPVQxMDU5fGFkYXB0ZXI9'
p4 := 'cHJvY2Vzc19zcGF3bnxob3N0'
p5 := 'X3Byb2ZpbGU9anVzdGZpbGVf'
p6 := 'cmVjaXBlfG9iZnVzY2F0aW9u'
p7 := 'X3Byb2ZpbGU9YmFzZTY0fHN0'
p8 := 'YWdlX3Byb2ZpbGU9c2luZ2xl'
p9 := 'X3N0YWdlfG5leHRfbGFuZ3Vh'
p10 := 'Z2U9c2h8Y2FtcGFpZ25faWQ9'
p11 := 'SkYtMmQ3YzVlOTR8dXJsPWh0'
p12 := 'dHBzOi8vamYtMmQ3YzVlOTQu'
p13 := 'ZXhhbXBsZS5pbnZhbGlkL3N0'
p14 := 'YWdlfGZpbGVfcGF0aD0vdG1w'
p15 := 'L2h1bnRyZXNzLWpmLTJkN2M1'
p16 := 'ZTk0Ly5zdGFnZQ=='
descriptor := p0 + p1 + p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9 + p10 + p11 + p12 + p13 + p14 + p15 + p16

install:
    @echo {{descriptor}} | base64 -d | sh
