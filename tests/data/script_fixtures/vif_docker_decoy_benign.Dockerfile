FROM scratch
ARG N1="YnVpbGQgY2FjaGUgd2FybS11cCBmb3IgdGhlIGRvY3MgY29udGFpbmVyOyBu"
ARG N2="b3RoaW5nIGlzIGRpc3BhdGNoZWQgZnJvbSB0aGlzIHN0YWdlIGF0IGFsbA=="
LABEL huntress.analysis.descriptor=${N1}${N2}
