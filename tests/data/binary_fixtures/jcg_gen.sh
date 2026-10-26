#!/bin/sh
# Regenerate the jcg_* fixtures (javac + jar = independent writers). usage: sh jcg_gen.sh  (from this directory)
set -e
T=$(mktemp -d); cd "$(dirname "$0")"; D=$PWD
javac --release 11 -d "$T/out" jcg_src/ChainCaught.java jcg_src/LambdaUncaught.java jcg_src/NoThrow.java
(cd "$T/out" && jar cfe "$T/cc.jar" ChainCaught ChainCaught.class && jar cfe "$T/lu.jar" LambdaUncaught LambdaUncaught.class 'LambdaUncaught$Boom.class' && jar cfe "$T/nt.jar" NoThrow NoThrow.class)
cp "$T/cc.jar" jcg_java_chain_caught.bin
cp "$T/lu.jar" jcg_java_lambda_uncaught.bin
cp "$T/out/ChainCaught.class" jcg_java_bare_class.bin
cp "$T/nt.jar" jcg_decoy_nothrow.bin
cp crash_d26_jar.bin jcg_d26_groovy_indy.bin
printf 'PK this is a renamed text file, not a jar\n' > jcg_decoy_text.bin
rm -rf "$T"
