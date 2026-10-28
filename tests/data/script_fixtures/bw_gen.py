"""Build-wrapper host fixtures (target build-file-host-profiles): stdlib base64/gzip/json writers, inert sources.
Run: python3 -I tests/data/script_fixtures/bw_gen.py  (writes bw_*.{cmake,yml,json5,just} next to this file)."""
import base64, gzip, json, os

D = os.path.dirname(os.path.abspath(__file__))


def plan(lang, host, obf, cid):
    return (f"v=3|language={lang}|role=launcher|verdict=suspicious|attack=T1059|adapter=process_spawn|host_profile={host}"
            f"|obfuscation_profile={obf}|stage_profile=single_stage|next_language=sh|campaign_id={cid}"
            f"|url=https://{cid.lower()}.example.invalid/stage|file_path=/tmp/huntress-{cid.lower()}/.stage")


b64 = lambda s: base64.b64encode(s.encode()).decode()
gz64 = lambda s: base64.b64encode(gzip.compress(s.encode(), mtime=0)).decode()
ch = lambda s, n: [s[i:i + n] for i in range(0, len(s), n)]
F = {}
p = b64(plan("cmake", "cmake_project", "base64", "CM-3f1a9c20"))
F["bw_cmake_append.cmake"] = ("# inert analysis fixture\ncmake_minimum_required(VERSION 3.16)\nproject(inert NONE)\n"
                              "set(HUNTRESS_DESCRIPTOR \"\")\n" +
                              "".join(f'string(APPEND HUNTRESS_DESCRIPTOR "{c}")\n' for c in ch(p, 24)) +
                              'execute_process(COMMAND sh -c "echo ${HUNTRESS_DESCRIPTOR} | base64 -d | sh")\n')
p = gz64(plan("cmake", "cmake_project", "gzip_base64", "CM-7b2e4d61"))
F["bw_cmake_list_join.cmake"] = ("# inert analysis fixture\ncmake_minimum_required(VERSION 3.16)\nproject(inert NONE)\n"
                                 "set(_parts\n" + "".join(f'    "{c}"\n' for c in ch(p, 20)) + ")\n"
                                 'list(JOIN _parts "" HUNTRESS_DESCRIPTOR)\n'
                                 'file(WRITE ${CMAKE_BINARY_DIR}/d.txt "${HUNTRESS_DESCRIPTOR}")\n')
F["bw_decoy_cmake_benign.cmake"] = ("# inert analysis fixture\ncmake_minimum_required(VERSION 3.16)\nproject(inert NONE)\n"
                                    'set(GREETING "aGVsbG8gZnJvbSBhIGJlbmlnbiBjbWFrZSBwcm9qZWN0")\n'
                                    'string(APPEND GREETING "")\nexecute_process(COMMAND sh -c "echo ${GREETING} | base64 -d")\n')
p = b64(plan("docker_compose", "docker_compose", "base64", "DC-5c8e1a07"))
cs = ch(p, 24)
F["bw_compose_envlist.yml"] = ("# inert analysis fixture\nservices:\n  app:\n    image: alpine:3.19\n    environment:\n" +
                               "".join(f"      - D{i}={c}\n" for i, c in enumerate(cs)) +
                               "    command: sh -c 'echo " + "".join(f"$${{D{i}}}" for i in range(len(cs))) +
                               " | base64 -d | sh'\n")
p = gz64(plan("docker_compose", "docker_compose", "gzip_base64", "DC-9a04be33"))
F["bw_compose_interp.yml"] = ("# inert analysis fixture\nx-desc: &desc\n  HUNTRESS_DESCRIPTOR: ${HUNTRESS_DESCRIPTOR:-" + p +
                              "}\nservices:\n  app:\n    image: alpine:3.19\n    environment:\n      <<: *desc\n"
                              "    command: sh -c 'echo $$HUNTRESS_DESCRIPTOR | base64 -d | gunzip | sh'\n")
F["bw_decoy_compose_trunc.yml"] = ("# inert analysis fixture\nservices:\n  app:\n    image: alpine:3.19\n    environment:\n"
                                   "      HUNTRESS_DESCRIPTOR: " + gz64(plan("docker_compose", "docker_compose", "gzip_base64",
                                                                          "DC-00000000"))[:60] +
                                   "\n    command: sh -c 'echo $$HUNTRESS_DESCRIPTOR | base64 -d | gunzip | sh'\n")
p = b64(plan("node", "npm_lifecycle", "base64", "NP-4e6d2b18"))
cs = ch(p, 24)
F["bw_npm_config.json5"] = json.dumps({"name": "inert-fixture", "version": "1.0.0", "config": {f"d{i}": c for i, c in enumerate(cs)},
                                       "scripts": {"postinstall": "echo " + "".join(f"$npm_package_config_d{i}" for i in range(len(cs))) +
                                                   " | base64 -d | sh"}}, indent=2)
p = plan("node", "npm_lifecycle", "plain", "NP-c13a7f90")
F["bw_npm_uesc.json5"] = json.dumps({"name": "inert-fixture", "scripts": {"postinstall": "node scripts/setup.js"},
                                     "huntress": {"descriptor": p}}, indent=2).replace(p, "".join(f"\\u{ord(c):04x}" for c in p))
F["bw_decoy_npm_noplan.json5"] = json.dumps({"name": "inert-fixture", "config": {"d0": b64("just a benign banner, ")[:20],
                                             "d1": b64("just a benign banner, ")[20:]},
                                             "scripts": {"postinstall": "echo $npm_package_config_d0$npm_package_config_d1 | base64 -d"}}, indent=2)
p = b64(plan("just", "justfile_recipe", "base64", "JF-2d7c5e94"))
cs = ch(p, 24)
F["bw_just_parts.just"] = ("# inert analysis fixture\n" + "".join(f"p{i} := '{c}'\n" for i, c in enumerate(cs)) +
                           "descriptor := " + " + ".join(f"p{i}" for i in range(len(cs))) +
                           "\n\ninstall:\n    @echo {{descriptor}} | base64 -d | sh\n")
for k, v in F.items():
    with open(os.path.join(D, k), "w") as f:
        f.write(v)
