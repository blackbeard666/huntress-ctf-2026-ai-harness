# inert analysis fixture: multi-stage build graph
ARG BASE=wordpress:cli
ARG TAIL=c3VzcGljaW91c3xhdHRhY2s9VDE2MTB8YWRhcHRlcj1wcm9jZXNzX3NwYXdufGhvc3RfcHJvZmlsZT1tdWx0aV9zdGFnZXxvYmZ1c2NhdGlvbl9wcm9maWxlPWJhc2U2NHxzdGFnZV9wcm9maWxlPWNvcHlfZnJvbXxuZXh0X2xhbmd1YWdlPXBvd2Vyc2hlbGw=
FROM ${BASE} AS builder
ARG TAIL
ENV HEAD=dj0zfGxhbmd1YWdlPWRvY2tlcmZpbGV8cm9sZT1idWlsZGVyfHZlcmRpY3Q9
USER root
RUN mkdir -p /out && \
    echo "${HEAD}${TAIL}" | base64 -d > /out/plan.txt

FROM builder AS lint
ENV HEAD=QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFB
RUN echo "${HEAD}${TAIL}" > /tmp/lint.txt

FROM scratch AS analysis_3fa9c2d1
COPY --from=builder /out/plan.txt /plan.txt
LABEL org.huntress.plan.stage="builder" org.huntress.plan.path="/plan.txt"
