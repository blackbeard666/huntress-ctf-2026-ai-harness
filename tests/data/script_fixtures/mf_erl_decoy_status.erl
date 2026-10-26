#!/usr/bin/env escript
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
