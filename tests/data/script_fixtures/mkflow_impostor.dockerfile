FROM alpine:3.20
ARG HUNTRESS_DESCRIPTOR_0badf00d=deadbeef
RUN echo build && make all
CMD ["/bin/sh", "-c", "echo run"]
