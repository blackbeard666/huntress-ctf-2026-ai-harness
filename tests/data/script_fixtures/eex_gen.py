"""Generator for the eex_* fixtures (target eex-heex-template-carrier): stdlib base64/binascii ENCODE of each plan into
Phoenix carriers -- an `.html.eex` template (tight `<%#..%>` EEx comment marker), a HEEx `~H` component with a wrapped
`<%!-- .. --%>` marker, and a `mix.exs` whose `aliases:` keyword list declares a `cmd` build-time pipeline. Expected
plains come from independent readers (EEx.tokenize / Code.string_to_quoted + sh; see each fixture's oracle_cmd)."""
import base64, binascii, json, pathlib
D = pathlib.Path(__file__).resolve().parent


def plan(role, attack, cid, url, path, nxt, prof="elixir_phoenix"):
    return (f"v=3|language=elixir|role={role}|verdict=suspicious|attack={attack}|adapter=process_spawn|"
            f"host_profile={prof}|obfuscation_profile=hex_base64|stage_profile=two_stage_download_execute|"
            f"next_language={nxt}|stage_count=2|steps=acquire_remote,dispatch_process|campaign_id={cid}|"
            f"url={url}|file_path={path}")


hb64 = lambda p: binascii.hexlify(base64.b64encode(p.encode())).decode()
b64 = lambda s: base64.b64encode(s.encode()).decode()

# T1: single grammar, `.html.eex` template, tight EEx comment `<%#HUNTRESS_ANALYSIS_V1:HB64-..%>` (no spaces)
p1 = plan("downloader", "T1105", "ELIXIR-3c9a17e2", "https://elixir-3c9a17e2b4.example.invalid/stage",
          "/tmp/huntress-elixir/.3c9a17e2b40d55aa.stage", "jscript")
(D / "eex_tpl_tight_comment.html.eex").write_text(f"""<%#HUNTRESS_ANALYSIS_V1:HB64-{hb64(p1)}%>
<section class="stage">
  <h1><%= @title %></h1>
  <div data-stage="<%= @descriptor %>"><%= render_inert(@conn) %></div>
</section>
""")

# T2: timed grammar, HEEx `~H` sigil in a function component, `<%!--` marker wrapped over indented lines
p2 = plan("launcher", "T1059", "ELIXIR-a41f0c", "https://elixir-a41f0c77d2.example.invalid/stage",
          "/tmp/huntress-elixir/.a41f0c77d2e81b39.stage", "bash")
m2 = hb64(p2)
wrapped = "\n".join("      " + m2[i:i + 72] for i in range(64, len(m2), 72))
(D / "eex_heex_wrapped_comment.ex").write_text(f'''defmodule HuntressWeb.StageComponentsa41f0c do
  use Phoenix.Component

  attr :descriptor, :string, default: nil

  def stage(assigns) do
    ~H"""
    <%!-- HUNTRESS_ANALYSIS_V1:HB64-{m2[:64]}
{wrapped}
    --%>
    <div id="stage" data-descriptor={{@descriptor}}>{{@descriptor}}</div>
    """
  end
end
''')

# T3: single grammar, mix.exs `aliases:` keyword list declaring a build-time `cmd` pipeline (compilers: hook)
p3 = plan("staged-chain", "T1105", "ELIXIR-77d0e5b1", "https://elixir-77d0e5b1c3.example.invalid/stage",
          "/tmp/huntress-elixir/.77d0e5b1c3f2a904.stage", "python")
(D / "eex_mix_alias_cmd.exs").write_text(f'''defmodule HuntressStage.MixProject do
  use Mix.Project

  def project do
    [
      app: :huntress_stage,
      version: "0.1.0",
      compilers: [:phoenix] ++ Mix.compilers(),
      aliases: aliases()
    ]
  end

  defp aliases do
    [
      setup: ["deps.get"],
      "compile.stage": ["cmd echo {b64(p3)} | base64 -d"]
    ]
  end
end
''')

# T4: DECOY, EEx/HEEx comments and a mix alias that carry no plan
(D / "eex_decoy_inert.html.heex").write_text('''<%# status=ok %>
<%!-- HUNTRESS_ANALYSIS_V1:NOTE-inert-analysis-fixture --%>
<div class="inert" data-descriptor={@descriptor}><%= @title %></div>
<% # mix alias: "cmd echo aW5lcnQtYW5hbHlzaXMtZml4dHVyZQ== | base64 -d" %>
''')

for stem, p in (("eex_tpl_tight_comment", p1), ("eex_heex_wrapped_comment", p2), ("eex_mix_alias_cmd", p3),
                ("eex_decoy_inert", None)):
    print(stem, json.dumps(p))
