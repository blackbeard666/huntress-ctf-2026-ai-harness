# Oracle reader for cfgchain fixtures: prints "key\tvalue" leaf lines of one Elixir config (.exs, via the real
# Config.Reader) or Erlang sys.config (via :file.consult). Leaves of keyword lists / maps / {atom, v} tuples.
defmodule Leaf do
  def kw?(l) when is_list(l) and l != [], do: Enum.all?(l, &match?({k, _} when is_atom(k), &1))
  def kw?(_), do: false
  def walk(%{} = m), do: Enum.flat_map(m, fn {k, v} -> pair(k, v) end)
  def walk(l) when is_list(l), do: Enum.flat_map(l, fn {k, v} -> pair(k, v); _ -> [] end)
  def pair(k, v) when is_map(v), do: walk(v) |> then(&(&1 == [] && [{k, v}] || &1))
  def pair(k, v) do
    if kw?(v), do: walk(v), else: [{k, v}]
  end
  def s(v) when is_binary(v), do: v
  def s(v) when is_atom(v), do: Atom.to_string(v)
  def s(v), do: inspect(v)
end
[path] = System.argv()
terms =
  if String.ends_with?(path, ".exs"),
    do: Config.Reader.read!(path, env: :prod),
    else: (with {:ok, [t]} <- :file.consult(String.to_charlist(path)), do: t)
seen = MapSet.new()
Enum.reduce(Leaf.walk(terms), seen, fn {k, v}, acc ->
  ks = Leaf.s(k)
  if MapSet.member?(acc, ks), do: acc, else: (IO.puts("#{ks}\t#{Leaf.s(v)}"); MapSet.put(acc, ks))
end)
