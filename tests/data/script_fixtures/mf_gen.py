"""actor-message-flow-model fixtures: stdlib-only writer of inert Erlang / Go message-passing sources.
The plan is split across messages; the oracle RUNS the real toolchain (escript / go run) and prints what the final
consumer assembled. Run: python3 -I tests/data/script_fixtures/mf_gen.py"""
import base64
import pathlib

D = pathlib.Path(__file__).resolve().parent
P1 = ("v=3|language=erlang|role=relay|verdict=suspicious|attack=T1059|adapter=process_spawn|host_profile=standalone|"
      "obfuscation_profile=base64|stage_profile=message_relay|next_language=bash|stage_count=2|"
      "steps=acquire_remote,dispatch_process|campaign_id=ERLANG-3c9a17e2|url=https://erlang-3c9a17e2b4.example.invalid/"
      "stage|file_path=/tmp/huntress-erlang/.3c9a17e2b4d01f66.stage")
P2 = ("v=3|language=go|role=collector|verdict=suspicious|attack=T1105|adapter=channel_fanin|host_profile=standalone|"
      "obfuscation_profile=hex|stage_profile=two_stage_download_execute|next_language=powershell|stage_count=2|"
      "steps=acquire_remote,write_file|campaign_id=GO-7d21e0aa|url=https://go-7d21e0aa91.example.invalid/stage|"
      "file_path=/tmp/huntress-go/.7d21e0aa91c4b3e2.stage")


def chunks(s, n):
    k = -(-len(s) // n)
    return [s[i:i + k] for i in range(0, len(s), k)]


# 1) Erlang: main -> relay ({part, N, Chunk}) -> collector ({chunk, N, Chunk}); sends are out of index order and the
#    collector sorts by index; a status/heartbeat process gets decoy text.
b = base64.b64encode(P1.encode()).decode()
c = chunks(b, 4)
order = [2, 0, 3, 1]
sends = "\n".join(f'    Relay ! {{part, {i + 1}, "{c[i]}"}},' for i in order)
(D / "mf_erl_relay_indexed.erl").write_text("""#!/usr/bin/env escript
%% inert analysis fixture: actor message flow (never executed by the harness)
% HUNTRESS_ANALYSIS_V1:B64-message-flow
-module(flow_3c9a17e2).
-mode(compile).

main(_) ->
    Self = self(),
    Collector = spawn(fun() -> collector(Self, []) end),
    register(sink, Collector),
    Relay = spawn(fun() -> relay(Collector) end),
    Status = spawn(fun() -> status() end),
    Status ! {heartbeat, "alive"},
@SENDS@
    Relay ! {flush, 4},
    receive
        {plan, Plan} -> io:format("~s~n", [Plan])
    after 2000 -> io:format("timeout~n")
    end.

relay(Next) ->
    receive
        {part, N, Chunk} -> Next ! {chunk, N, Chunk}, relay(Next);
        {flush, Count} -> Next ! {done, Count}
    end.

collector(Parent, Acc) ->
    receive
        {chunk, N, Data} -> collector(Parent, [{N, Data} | Acc]);
        {done, _} ->
            Joined = lists:append([D || {_, D} <- lists:keysort(1, Acc)]),
            Parent ! {plan, base64:decode(Joined)}
    end.

status() ->
    receive
        {heartbeat, _} -> status()
    after 100 -> ok
    end.
""".replace("@SENDS@", sends))

# 2) Go: producer goroutine sends hex chunks over a channel from a literal slice; main drains it (range) and decodes.
h = P2.encode().hex()
gc = chunks(h, 5)
lst = ", ".join(f'"{x}"' for x in gc)
(D / "mf_go_chan_range.go").write_text(f"""// inert analysis fixture: channel message flow (never executed by the harness)
// HUNTRESS_ANALYSIS_V1:HEX-message-flow
package main

import (
\t"encoding/hex"
\t"fmt"
\t"strings"
)

func producer(out chan<- string) {{
\tfor _, part := range []string{{{lst}}} {{
\t\tout <- part
\t}}
\tclose(out)
}}

func main() {{
\tch := make(chan string)
\tgo producer(ch)
\tvar sb strings.Builder
\tfor part := range ch {{
\t\tsb.WriteString(part)
\t}}
\tb, _ := hex.DecodeString(sb.String())
\tfmt.Println(string(b))
}}
""")

# 3) DECOY: same Erlang shape, but the messages carry status text only (no plan anywhere).
(D / "mf_erl_decoy_status.erl").write_text("""#!/usr/bin/env escript
%% inert analysis fixture: actor message flow decoy (never executed by the harness)
-module(flow_decoy).
-mode(compile).

main(_) ->
    Self = self(),
    Worker = spawn(fun() -> worker(Self) end),
    Worker ! {status, "ready"},
    Worker ! {status, "v=3 is not a plan"},
    Worker ! {stop, "bye"},
    receive
        {ack, Text} -> io:format("~s~n", [Text])
    after 2000 -> io:format("timeout~n")
    end.

worker(Parent) ->
    receive
        {status, _} -> worker(Parent);
        {stop, Why} -> Parent ! {ack, Why}
    end.
""")
print(P1)
print(P2)
