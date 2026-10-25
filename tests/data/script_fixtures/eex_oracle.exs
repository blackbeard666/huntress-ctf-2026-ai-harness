# Oracle for eex_* fixtures (real Elixir 1.18 parser + EEx tokenizer; nothing in the fixture is evaluated).
#   comments <file>: every `~H"""` sigil body (or the whole file when it is not Elixir source) -> EEx.tokenize ->
#                    each `<%!-- --%>` comment token, whitespace removed, one per line
#   aliases <file>:  the `aliases` keyword list of a mix.exs (Code.string_to_quoted) -> each "cmd .." task, one per line
[mode, file] = System.argv()
src = File.read!(file)
case mode do
  "comments" ->
    bodies =
      case Code.string_to_quoted(src) do
        {:ok, ast} ->
          {_, acc} = Macro.prewalk(ast, [], fn
            {:sigil_H, _, [{:<<>>, _, [body]}, _]} = n, acc -> {n, [body | acc]}
            n, acc -> {n, acc}
          end)
          Enum.reverse(acc)
        _ -> [src]
      end
    for b <- bodies, {:ok, toks} = EEx.tokenize(String.to_charlist(b)), {:comment, c, _} <- toks,
        do: IO.puts(String.replace(List.to_string(c), ~r/\s+/, ""))
  "aliases" ->
    {_, acc} = Code.string_to_quoted!(src) |> Macro.prewalk([], fn
      {:defp, _, [{:aliases, _, _}, [do: kw]]} = n, acc -> {n, [kw | acc]}
      n, acc -> {n, acc}
    end)
    for kw <- acc, {_task, cmds} <- kw, c <- List.wrap(cmds), is_binary(c), String.starts_with?(c, "cmd "),
        do: IO.puts(String.replace_prefix(c, "cmd ", ""))
end
