# Oracle for beam_ex_* fixtures: parse with the real Elixir parser, Code.eval_quoted ONLY the expression bound to
# `@descriptor_*` / `descriptor_* =` (nothing else in the file runs); print the value raw.
[file] = System.argv()
ast = file |> File.read!() |> Code.string_to_quoted!()
{_, found} =
  Macro.prewalk(ast, nil, fn
    {:@, _, [{name, _, [expr]}]} = n, nil when is_atom(name) ->
      {n, if(String.starts_with?(Atom.to_string(name), "descriptor_"), do: expr)}
    {:=, _, [{name, _, ctx}, expr]} = n, nil when is_atom(name) and is_atom(ctx) ->
      {n, if(String.starts_with?(Atom.to_string(name), "descriptor_"), do: expr)}
    n, acc -> {n, acc}
  end)
{value, _} = Code.eval_quoted(found)
IO.write(value)
