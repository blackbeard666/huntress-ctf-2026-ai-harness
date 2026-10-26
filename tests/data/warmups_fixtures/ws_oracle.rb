# Independent Whitespace interpreter (oracle for the ws-lang fixtures). Usage: ruby ws_oracle.rb raw|stl|bracket FILE
# Prints the program's output, or "none" when the source does not parse/run as Whitespace.
mode, path = ARGV
src = File.binread(path).force_encoding("UTF-8")
code = case mode
       when "stl" then src.gsub(/[^STLN]/, "").tr("N", "L")
       when "bracket" then src.scan(/\[(Space|Tab|LF)\]/i).map { |m| { "space" => "S", "tab" => "T", "lf" => "L" }[m[0].downcase] }.join
       else src.gsub(/[^ \t\n]/, "").tr(" \t\n", "STL")
       end
pos = 0
take = ->(s) { if code[pos, s.size] == s then pos += s.size; true else false end }
readnum = lambda do
  e = code.index("L", pos) or raise "unterminated"
  t = code[pos...e]; pos = e + 1
  v = t[1..].to_s.tr("ST", "01").to_i(2)
  t[0] == "T" ? -v : v
end
readlab = lambda do
  e = code.index("L", pos) or raise "unterminated"
  t = code[pos...e]; pos = e + 1; t
end
ins, marks = [], {}
begin
  while pos < code.size
    if take.("SS") then ins << [:push, readnum.()]
    elsif take.("SLS") then ins << [:dup]
    elsif take.("SLT") then ins << [:swap]
    elsif take.("SLL") then ins << [:drop]
    elsif take.("STS") then ins << [:copy, readnum.()]
    elsif take.("STL") then ins << [:slide, readnum.()]
    elsif take.("TSSS") then ins << [:add]
    elsif take.("TSST") then ins << [:sub]
    elsif take.("TSSL") then ins << [:mul]
    elsif take.("TSTS") then ins << [:div]
    elsif take.("TSTT") then ins << [:mod]
    elsif take.("TTS") then ins << [:store]
    elsif take.("TTT") then ins << [:fetch]
    elsif take.("LSS") then marks[readlab.()] = ins.size
    elsif take.("LST") then ins << [:call, readlab.()]
    elsif take.("LSL") then ins << [:jmp, readlab.()]
    elsif take.("LTS") then ins << [:jz, readlab.()]
    elsif take.("LTT") then ins << [:jn, readlab.()]
    elsif take.("LTL") then ins << [:ret]
    elsif take.("LLL") then ins << [:end]
    elsif take.("TLSS") then ins << [:putc]
    elsif take.("TLST") then ins << [:putn]
    else raise "bad op at #{pos}"
    end
  end
  stack, heap, rets, out, ip, n = [], Hash.new(0), [], +"", 0, 0
  while ip < ins.size
    (n += 1) > 1_000_000 and raise "step cap"
    op, a = ins[ip]; ip += 1
    case op
    when :push then stack.push(a)
    when :dup then stack.push(stack.fetch(-1))
    when :swap then x = stack.pop; y = stack.pop; stack.push(x, y)
    when :drop then stack.pop
    when :copy then stack.push(stack.fetch(-1 - a))
    when :slide then x = stack.pop; stack.pop(a); stack.push(x)
    when :add, :sub, :mul, :div, :mod
      b = stack.pop; x = stack.pop
      stack.push({ add: x + b, sub: x - b, mul: x * b, div: b.zero? ? raise("div0") : x / b, mod: b.zero? ? 0 : x % b }[op])
    when :store then v = stack.pop; heap[stack.pop] = v
    when :fetch then stack.push(heap[stack.pop])
    when :call then rets.push(ip); ip = marks.fetch(a)
    when :jmp then ip = marks.fetch(a)
    when :jz then ip = marks.fetch(a) if stack.pop == 0
    when :jn then ip = marks.fetch(a) if stack.pop < 0
    when :ret then ip = rets.pop
    when :end then break
    when :putc then out << stack.pop.chr(Encoding::UTF_8)
    when :putn then out << stack.pop.to_s
    end
  end
  raise "no output" if out.strip.empty? || out =~ /[\x00-\x08\x0e-\x1f]/
  print out
rescue StandardError, TypeError
  print "none"
end
