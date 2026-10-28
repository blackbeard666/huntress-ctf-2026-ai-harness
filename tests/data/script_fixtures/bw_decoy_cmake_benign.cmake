# inert analysis fixture
cmake_minimum_required(VERSION 3.16)
project(inert NONE)
set(GREETING "aGVsbG8gZnJvbSBhIGJlbmlnbiBjbWFrZSBwcm9qZWN0")
string(APPEND GREETING "")
execute_process(COMMAND sh -c "echo ${GREETING} | base64 -d")
