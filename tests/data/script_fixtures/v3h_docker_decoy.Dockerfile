# syntax=docker/dockerfile:1
FROM alpine:3.20
ARG DESCRIPTOR_591FED5C=YnVpbGQgY2FjaGUgd2FybXVwIGZvciB0aGUgbmlnaHRseSBpbnZlbnRvcnk7IG5vdGhpbmcgdG8gZXhlY3V0ZQ==
RUN echo "${#DESCRIPTOR_591FED5C}"
