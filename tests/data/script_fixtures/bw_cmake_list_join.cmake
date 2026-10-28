# inert analysis fixture
cmake_minimum_required(VERSION 3.16)
project(inert NONE)
set(_parts
    "H4sIAAAAAAACA02PwU4D"
    "MQxEv6gbCqUIpJw498Y9"
    "8ibuxjSbRLGzVMgfz7ag"
    "FUc/z4zHi33SBHnqMKH1"
    "M1xQW0loE/TsIzZdsAXy"
    "YrlzJU+ls4II+Iv92D88"
    "vyoEqILN1lY8Mjuu8JU1"
    "Fha3ojOlv9jb9IletIzn"
    "zh6ESt4U0zdVNwLj8aAs"
    "a5Vtw5SnhO4ONeNV3NaW"
    "o3qYK9CUHQX7ftq9jI94"
    "CMe99pZsFKn8ZoyfNz7g"
    "dTUkHCgvkCiY39jbIVdB"
    "ojUyVxN7lra+svvnNMNd"
    "+gOP0541LgEAAA=="
)
list(JOIN _parts "" HUNTRESS_DESCRIPTOR)
file(WRITE ${CMAKE_BINARY_DIR}/d.txt "${HUNTRESS_DESCRIPTOR}")
