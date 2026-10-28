# inert analysis fixture: benign multi-stage build (decoy)
ARG BASE=wordpress:cli
FROM ${BASE} AS build
ARG CONF=c2VydmVyIHsKICBsaXN0ZW4gODA4MDsKICByb290IC9zcnYvd3d3Owp9Cg==
USER root
RUN mkdir -p /out && echo "${CONF}" | base64 -d > /out/site.conf

FROM build AS test
ENV CHECK=H4sIAAAAAAAAAyuzNa7JScxLL00=
RUN echo "${CHECK}" > /tmp/check.txt

FROM scratch AS analysis_0c11d00d
COPY --from=build /out/site.conf /site.conf
