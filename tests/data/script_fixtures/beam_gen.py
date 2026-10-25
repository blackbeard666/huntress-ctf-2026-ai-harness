"""Generator for the beam_* fixtures (target beam-erlang-elixir-route): stdlib base64/binascii ENCODE of each plan into
Erlang / Elixir descriptor syntax. Expected plains come from the real interpreters (beam_oracle.escript / .exs)."""
import base64, binascii, pathlib, textwrap
D = pathlib.Path(__file__).resolve().parent


def plan(lang, role, attack, cid, url, path, nxt):
    return (f"v=3|language={lang}|role={role}|verdict=suspicious|attack={attack}|adapter=process_spawn|"
            f"host_profile=standalone|obfuscation_profile=hex_base64|stage_profile=two_stage_download_execute|"
            f"next_language={nxt}|stage_count=2|steps=acquire_remote,dispatch_process|campaign_id={cid}|"
            f"url={url}|file_path={path}")


hb64 = lambda p: binascii.hexlify(base64.b64encode(p.encode())).decode()
b64 = lambda s: base64.b64encode(s.encode()).decode()
ints = lambda s: ",".join(str(b) for b in s.encode())

# E1: escript, no marker; ?MACRO int-list charlist ++ "..", int binary, list_to_binary; os:cmd / open_port inert
p1 = plan("erlang", "launcher", "T1059", "ERLANG-5be0c417", "https://erlang-5be0c417aa.example.invalid/stage",
          "/tmp/huntress-erlang/.5be0c417aa61d2f0.stage", "bash")
m1 = hb64(p1)
a, b, c = m1[:60], m1[60:300], m1[300:]
(D / "beam_erl_escript_intlist.erl").write_text(f"""#!/usr/bin/env escript
%% -*- erlang -*-
%% inert analysis fixture: polyglot erlang launcher (never executed by the harness)
-mode(compile).
-define(PART_A, [{ints(a)}]).
-define(PART_C, <<{ints(c)}>>).

descriptor_5be0c417() ->
    list_to_binary(?PART_A ++ "{b[:120]}"
                   "{b[120:]}" ++ binary_to_list(?PART_C)).

main(_Args) ->
    _ = descriptor_5be0c417(),
    Cmd = "true",
    case os:getenv("HUNTRESS_NEVER") of
        "1" -> os:cmd(Cmd), open_port({{spawn, Cmd}}, []);
        _ -> ok
    end.
""")

# E2: -module, -define(DESCRIPTOR_..) binary segments with /utf8, base64:decode/1 over a b64 of the HB64 material
p2 = plan("erlang", "downloader", "T1105", "ERLANG-c03d9e11", "https://erlang-c03d9e11b7.example.invalid/stage",
          "/tmp/huntress-erlang/.c03d9e11b7f04a6e.stage", "powershell")
m2 = b64(hb64(p2))
(D / "beam_erl_module_define_b64.erl").write_text(f"""%% inert analysis fixture: polyglot erlang downloader
-module(polyglot_erlang_downloader).
-export([run/0, descriptor_c03d9e11/0]).

-define(DESCRIPTOR_C03D9E11, <<"{m2[:200]}"/utf8,
                                "{m2[200:]}">>).

descriptor_c03d9e11() -> base64:decode(?DESCRIPTOR_C03D9E11).

run() ->
    Plan = #{{descriptor => descriptor_c03d9e11()}},
    {{ok, Plan}}.
""")

# E3 decoy: same shape, the descriptor decodes to a status line (no plan)
(D / "beam_erl_decoy_status.erl").write_text(f"""%% inert analysis fixture: erlang decoy (no plan)
-module(polyglot_erlang_decoy).
-export([descriptor_9e0a1b2c/0]).

descriptor_9e0a1b2c() -> <<{ints(hb64("status=ok;inert-analysis-fixture;no plan here"))}>>.
""")

# X1: Elixir module attribute (no `=`) as a ~S heredoc of the chunked HB64 material; System.cmd inert
p3 = plan("elixir", "launcher", "T1059.004", "ELIXIR-71fa02d8", "https://elixir-71fa02d8c4.example.invalid/stage",
          "/tmp/huntress-elixir/.71fa02d8c4e93b15.stage", "python")
m3 = hb64(p3)
body = "\n".join("    " + ln for ln in textwrap.wrap(m3, 76))
(D / "beam_ex_attr_heredoc.exs").write_text(f"""# inert analysis fixture: polyglot elixir launcher (never executed by the harness)
defmodule Polyglot.Launcher do
  @moduledoc false
  @descriptor_71fa02d8 ~S\"\"\"
{body}
    \"\"\"

  def plan, do: %{{descriptor: @descriptor_71fa02d8}}

  def run(false), do: :ok
  def run(true), do: System.cmd("sh", ["-c", "true"])
end
""")

# X2: Elixir ~s() <> "" <> List.to_string(~c"") |> Base.decode64!() over a b64 of the HB64 material
p4 = plan("elixir", "downloader", "T1105", "ELIXIR-e2b95c60", "https://elixir-e2b95c6013.example.invalid/stage",
          "/tmp/huntress-elixir/.e2b95c6013a8f47d.stage", "jscript")
m4 = b64(hb64(p4))
(D / "beam_ex_sigil_pipe.exs").write_text(f"""# inert analysis fixture: polyglot elixir downloader
descriptor_e2b95c60 =
  ~s({m4[:180]}) <>
    "{m4[180:400]}" <>
    List.to_string(~c"{m4[400:]}")
  |> Base.decode64!()

_plan_e2b95c60 = %{{descriptor: descriptor_e2b95c60}}
if System.get_env("HUNTRESS_NEVER") == "1", do: System.cmd("curl", ["-fsS", "https://invalid.invalid"])
""")

# X3 decoy: Elixir attribute sigil decoding to a status line
(D / "beam_ex_decoy_status.exs").write_text(f"""# inert analysis fixture: elixir decoy (no plan)
defmodule Polyglot.Decoy do
  @descriptor_0d4c7e91 ~s({hb64("status=ok;inert-analysis-fixture;no plan here")})
  def plan, do: %{{descriptor: @descriptor_0d4c7e91}}
end
""")
