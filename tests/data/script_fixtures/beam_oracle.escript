%% Oracle for beam_erl_* fixtures: parse the .erl / escript with the real Erlang front end (epp, macros expanded) and
%% erl_eval ONLY the body of the 0-arity `descriptor_*` function (main/run are never called); print the value raw.
main([File]) ->
    {ok, Bin} = file:read_file(File),
    Src = case Bin of <<"#!", _/binary>> -> [_ | T] = binary:split(Bin, <<"\n">>), <<"%\n", (hd(T))/binary>>;
                      _ -> Bin end,
    Tmp = "/tmp/beam_oracle_" ++ os:getpid() ++ ".erl",
    ok = file:write_file(Tmp, Src),
    {ok, Forms} = epp:parse_file(Tmp, []),
    file:delete(Tmp),
    [Body] = [B || {function, _, Name, 0, [{clause, _, [], [], B}]} <- Forms,
                   lists:prefix("descriptor_", atom_to_list(Name))],
    {value, V, _} = erl_eval:exprs(Body, erl_eval:new_bindings()),
    io:put_chars(V).
