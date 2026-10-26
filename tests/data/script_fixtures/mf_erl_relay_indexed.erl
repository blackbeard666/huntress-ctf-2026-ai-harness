#!/usr/bin/env escript
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
    Relay ! {part, 3, "RhZ2VfY291bnQ9MnxzdGVwcz1hY3F1aXJlX3JlbW90ZSxkaXNwYXRjaF9wcm9jZXNzfGNhbXBhaWduX2lkPUVSTEFORy0zYzlhMTdlMnx1cmw9aHR0cHM6Ly9lc"},
    Relay ! {part, 1, "dj0zfGxhbmd1YWdlPWVybGFuZ3xyb2xlPXJlbGF5fHZlcmRpY3Q9c3VzcGljaW91c3xhdHRhY2s9VDEwNTl8YWRhcHRlcj1wcm9jZXNzX3NwYXdufGhvc3RfcHJ"},
    Relay ! {part, 4, "mxhbmctM2M5YTE3ZTJiNC5leGFtcGxlLmludmFsaWQvc3RhZ2V8ZmlsZV9wYXRoPS90bXAvaHVudHJlc3MtZXJsYW5nLy4zYzlhMTdlMmI0ZDAxZjY2LnN0YWdl"},
    Relay ! {part, 2, "vZmlsZT1zdGFuZGFsb25lfG9iZnVzY2F0aW9uX3Byb2ZpbGU9YmFzZTY0fHN0YWdlX3Byb2ZpbGU9bWVzc2FnZV9yZWxheXxuZXh0X2xhbmd1YWdlPWJhc2h8c3"},
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
