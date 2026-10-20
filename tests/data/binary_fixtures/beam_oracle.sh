#!/bin/bash
# usage: beam_oracle.sh file.bin -- INDEPENDENT reader: OTP's own beam_lib / escript:extract / zip / zlib / base64 /
# erlang:crc32 (no lib/binary.py). Prints: file -b | LitT zlib stream offset in the (extracted) .beam = 'LitT' + 12 (binary:match) | module |
# encoding | HCFG ver key len crc crc32(plain) | plain JSON   ("none" when no valid blob).
F=$(realpath "$1"); ERL=$(dirname "$(realpath "$0")")/../../../tools/erlang-dl/root/usr/lib/erlang/bin
export PATH="$ERL:$PATH"
FB=$(file -b "$F" | cut -c1-60)
R=$(erl -noshell -eval '
[F] = init:get_plain_arguments(),
{ok, Raw} = file:read_file(F),
Beam = case Raw of <<"FOR1", _/binary>> -> Raw; _ ->
  case catch escript:extract(F, []) of
    {ok, S} -> {archive, A} = lists:keyfind(archive, 1, S),
               {ok, Fs} = zip:extract(A, [memory]),
               hd([B || {N, B} <- Fs, filename:extension(N) == ".beam"]);
    _ -> none end end,
Out = case catch beam_lib:chunks(Beam, [atoms, "LitT"]) of
  {ok, {Mod, [{atoms, _}, {"LitT", <<_:32, Z/binary>>}]}} ->
    Lit = zlib:uncompress(Z),
    Try = fun(Blob) -> case Blob of
        <<"HCFG", V, K, L:16/little, C:32/little, Body:L/binary, _/binary>> ->
          P = << <<(X bxor K)>> || <<X>> <= Body >>,
          case erlang:crc32(P) of C -> {ok, io_lib:format("HCFG ~p ~p ~p ~p ~p | ~s", [V, K, L, C, erlang:crc32(P), P])}; _ -> bad end;
        _ -> bad end end,
    B64 = case re:run(Lit, "SENGR[A-Za-z0-9+/=]+", [{capture, first, binary}]) of
      {match, [T]} -> case catch base64:decode(T) of D when is_binary(D) -> Try(D); _ -> bad end; _ -> bad end,
    RawHit = case binary:match(Lit, <<"HCFG">>) of {S0, _} -> Try(binary:part(Lit, S0, byte_size(Lit) - S0)); _ -> bad end,
    {LitPos, _} = binary:match(Beam, <<"LitT">>), Off = integer_to_list(LitPos + 12),
    case {B64, RawHit} of {{ok, M}, _} -> [Off, " | ", atom_to_list(Mod), " | base64 | ", M];
                          {_, {ok, M}} -> [Off, " | ", atom_to_list(Mod), " | raw-in-zlib | ", M];
                          _ -> [Off, " | ", atom_to_list(Mod), " | none"] end;
  _ -> "none | none | none" end,
io:format("~s~n", [Out]), halt().' -extra "$F" 2>&1 | tail -1)
echo "$FB | $R"
