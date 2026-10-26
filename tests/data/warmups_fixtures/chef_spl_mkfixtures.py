"""Chef / Shakespeare (SPL) fixtures. Programs are written HERE (no lib import); `expected` comes from the independent
PyPI interpreters chef-lang 0.1.0 (chef_lang.interpreter.Chef) and shakespearelang 1.0.0 (Shakespeare.run), installed
with `pip install --target tools/esolang-oracles chef-lang shakespearelang`.
Run: python3 tests/data/warmups_fixtures/chef_spl_mkfixtures.py"""
import io
import json
import sys
import contextlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools" / "esolang-oracles"))
from chef_lang.interpreter import Chef, RecipeEnd  # noqa: E402
from shakespearelang import Shakespeare  # noqa: E402

GEN = "python3 tests/data/warmups_fixtures/chef_spl_mkfixtures.py   # program text written by this script"
CHEF_ORACLE = ("PYTHONPATH=tools/esolang-oracles python3 -c 'import sys; from chef_lang.interpreter import Chef, "
               "RecipeEnd; c=Chef(open(sys.argv[1]).read().rstrip()+chr(10)*2); c.parse_script(); ...; print(c.serve())' prog.chef"
               "   # chef-lang 0.1.0 (PyPI)")
SPL_ORACLE = ("PYTHONPATH=tools/esolang-oracles python3 -c 'import sys; from shakespearelang import Shakespeare; "
              "Shakespeare(open(sys.argv[1]).read()).run()' prog.spl   # shakespearelang 1.0.0 (PyPI)")
PLAIN = {
    "amber": "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: amber-otter-41",
    "jade": "Well cooked! Submit this exact answer to the Game Master: jade-heron-17",
    "cobalt": "To solve, submit this exact answer to the Game Master: cobalt-raven-58",
    "maple": "Bravo! Submit this exact answer to the Game Master: maple-finch-23",
}


def chef_oracle(prog):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            c = Chef(prog.rstrip("\n") + "\n\n")   # chef-lang needs a blank line after 'Serves N.'
            c.parse_script()
            try:
                c.execute_script()
                print(c.serve(), end="")
            except RecipeEnd:
                pass
    except Exception as e:  # noqa: BLE001 - a decoy is expected to be rejected by the oracle too
        return None, f"{type(e).__name__}: {e}"
    return buf.getvalue(), ""


def spl_oracle(prog):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            Shakespeare(prog).run()
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {str(e)[:120]}"
    return buf.getvalue(), ""


FOODS = ["haricot beans", "eggs", "lard", "oil", "zucchinis", "water", "red salmon", "dijon mustard", "potatoes",
         "flour", "sugar", "butter", "milk", "salt", "honey", "cocoa", "vanilla", "yeast", "cream", "cheese", "garlic",
         "onions", "carrots", "rice", "pepper", "basil", "thyme", "lemons", "apples", "pears", "plums", "raisins",
         "almonds", "walnuts", "oats", "barley", "ginger", "nutmeg", "cloves", "mint", "dates", "figs", "peas"]
MEAS = ["g", "", "g", "cups", "", "ml", "g", "g", "", "kg", "pinches", "dashes", "teaspoons", "tablespoons", "l"]


def souffle(s, title):
    """The 'Hello World Souffle' shape: one ingredient per distinct char with mixed measures, Put back to front,
    Liquefy the bowl, Pour into the dish, Serves 1."""
    names, ings = {}, []
    for ch in s:
        if ch not in names:
            k = len(names)
            names[ch] = FOODS[k]
            m = MEAS[k % len(MEAS)]
            ings.append(f"{ord(ch)} {m} {FOODS[k]}".replace("  ", " "))
    meth = "\n".join(f"Put {names[ch]} into the mixing bowl." for ch in reversed(s))
    return (f"{title}.\n\nThis recipe prints a sentence, in a basically brute force way.\n\nIngredients.\n"
            + "\n".join(ings) + "\n\nMethod.\n" + meth + "\nLiquefy contents of the mixing bowl.\n"
            "Pour contents of the mixing bowl into the baking dish.\n\nServes 1.\n")


WORDS = "zero one two three four five six seven eight nine ten eleven twelve".split()


def loop_chef(s, title):
    """Loop-built chars: code = 10*q + r; per char push 0, load q into 'counter' via the 2nd bowl (Put + Fold), loop
    'Whisk the counter. Add tens. Whisk the counter until whisked.', then Add the remainder. Every bowl is numbered
    (chef-lang rejects an unnumbered bowl once a numbered one is used)."""
    qs = sorted({ord(c) // 10 for c in s})
    rs = sorted({ord(c) % 10 for c in s})
    ings = (["0 g nothing", "10 g tens", "0 g counter"] + [f"{q} g {WORDS[q]} flour" for q in qs]
            + [f"{r} ml {WORDS[r]} milk" for r in rs])
    steps = []
    for ch in reversed(s):
        q, r = divmod(ord(ch), 10)
        steps += ["Put nothing into the 1st mixing bowl.", f"Put {WORDS[q]} flour into the 2nd mixing bowl.",
                  "Fold counter into the 2nd mixing bowl.", "Whisk the counter.", "Add tens to the 1st mixing bowl.",
                  "Whisk the counter until whisked.", f"Add {WORDS[r]} milk to the 1st mixing bowl."]
    steps += ["Liquefy contents of the 1st mixing bowl.", "Pour contents of the 1st mixing bowl into the 1st baking dish."]
    return f"{title}.\n\nIngredients.\n" + "\n".join(ings) + "\n\nMethod.\n" + "\n".join(steps) + "\n\nServes 1.\n"


ADJ = ["big", "huge", "furry", "old", "green", "large", "tiny", "red", "white", "bottomless"]
POS = ["cat", "horse", "rose", "flower", "pony", "King", "tree", "moon"]
NEG = ["pig", "toad", "hog", "wolf", "coward", "devil", "goat", "plague"]


def np_(k, neg=False, salt=0):
    adjs = " ".join(ADJ[(salt + i) % len(ADJ)] for i in range(k))
    noun = (NEG if neg else POS)[(salt + k) % 8]
    return ("the " if neg else "a ") + (adjs + " " if adjs else "") + noun


def bits_expr(v, neg=False, salt=0):
    bits = [k for k in range(v.bit_length()) if v >> k & 1]
    e = np_(bits[-1], neg, salt)
    for k in reversed(bits[:-1]):
        e = f"the sum of {np_(k, neg, salt + k)} and {e}"
    return e


def spl_delta(s, title):
    """Delta play: Hamlet and Ophelia take turns; each sets the other relative to its old value ('You are the sum of
    yourself and <+np>' / 'the difference between yourself and <np>' / negative nouns), then 'Speak your mind!'."""
    cur = {"Hamlet": 0, "Ophelia": 0}
    lines = []
    for i, ch in enumerate(s):
        spk, lis = ("Hamlet", "Ophelia") if i % 2 == 0 else ("Ophelia", "Hamlet")
        d = ord(ch) - cur[lis]
        if d == 0:
            st = "You are as good as yourself!"
        elif d > 0:
            st = f"You are the sum of yourself and {bits_expr(d, salt=i)}!"
        elif i % 3:
            st = f"You are the difference between yourself and {bits_expr(-d, salt=i)}!"
        else:
            st = f"You are the sum of thyself and {bits_expr(-d, neg=True, salt=i)}!"
        cur[lis] = ord(ch)
        lines.append(f"{spk}:\n {st} Speak your mind!")
    return (f"{title}.\n\nHamlet, a melancholy prince.\nOphelia, a lady of the court.\n\n"
            "                    Act I: The letter.\n\n                    Scene I: The reading.\n\n"
            "[Enter Hamlet and Ophelia]\n\n" + "\n\n".join(lines) + "\n\n[Exeunt]\n")


def spl_abs(s, title):
    """Absolute play with a Remember/Recall stack and a scene goto: Romeo pushes every char's code (absolute
    powers-of-two noun phrases) onto Juliet's stack back to front, then a loop scene pops and speaks them until a
    zero sentinel, asking 'Is she as good as nothing?'."""
    lines = ["Romeo:\n You are nothing! Remember yourself!"]
    for ch in reversed(s):
        lines.append(f"Romeo:\n You are as lovely as {bits_expr(ord(ch))}! Remember yourself!")
    return (f"{title}.\n\nRomeo, a young man of Verona.\nJuliet, a likewise young woman.\n\n"
            "Act I: Romeo's devotion.\n\nScene I: The stacking of words.\n\n[Enter Romeo and Juliet]\n\n"
            + "\n\n".join(lines) + "\n\nScene II: The reading of words.\n\nRomeo:\n Recall your sweet words!\n"
            " Are you as good as nothing?\n\nRomeo:\n If not, speak your mind! If not, let us return to scene II.\n\n"
            "[Exeunt]\n")


def main():
    out = []
    hello = ("Hello World Souffle.\n\nThis recipe prints the immortal words \"Hello world!\", in a basically brute "
             "force way. It also makes a lot of food for one person.\n\nIngredients.\n72 g haricot beans\n101 eggs\n"
             "108 g lard\n111 cups oil\n32 zucchinis\n119 ml water\n114 g red salmon\n100 g dijon mustard\n33 potatoes"
             "\n\nMethod.\nPut potatoes into the mixing bowl.\nPut dijon mustard into the mixing bowl.\nPut lard into "
             "the mixing bowl.\nPut red salmon into the mixing bowl.\nPut oil into the mixing bowl.\nPut water into the "
             "mixing bowl.\nPut zucchinis into the mixing bowl.\nPut oil into the mixing bowl.\nPut lard into the mixing "
             "bowl.\nPut lard into the mixing bowl.\nPut eggs into the mixing bowl.\nPut haricot beans into the mixing "
             "bowl.\nLiquefy contents of the mixing bowl.\nPour contents of the mixing bowl into the baking dish.\n\n"
             "Serves 1.\n")
    cases = [
        ("chef-hello-world-souffle", "chef", hello, None, "verbatim 'Hello World Souffle' (David Morgan-Mar, esolangs wiki)"),
        ("chef-souffle-amber", "chef", souffle(PLAIN["amber"], "Food for Thought Souffle"), PLAIN["amber"], GEN),
        ("chef-loops-jade", "chef", loop_chef(PLAIN["jade"], "Whisked Warmup Pudding"), PLAIN["jade"], GEN),
        ("chef-decoy-plain-recipe", "chef",
         "Simple Pancakes.\n\nIngredients.\n200 g flour\n2 eggs\n300 ml milk\n1 pinch salt\n\n"
         "Whisk the flour, eggs and milk until smooth. Rest the batter for 30 minutes, then fry thin pancakes "
         "in a hot buttered pan.\n\nServes 4.\n", None, "printf %s '<plain English recipe: Ingredients, no Method>'"),
        ("chef-decoy-prose-method", "chef",
         "Tomato Soup.\n\nIngredients.\n6 tomatoes\n1 onions\n500 ml stock\n\nMethod.\nChop the onions finely. "
         "Simmer the tomatoes with the stock for twenty minutes. Blend until smooth and season to taste.\n\n"
         "Serves 2.\n", None, "printf %s '<English recipe whose Method is ordinary cooking prose>'"),
        ("spl-delta-cobalt", "shakespeare", spl_delta(PLAIN["cobalt"], "The Tragedy of the Warmup"), PLAIN["cobalt"], GEN),
        ("spl-stack-goto-maple", "shakespeare", spl_abs(PLAIN["maple"], "Romeo and the Remembered Words"),
         PLAIN["maple"], GEN),
        ("spl-decoy-real-hamlet", "shakespeare",
         "The Tragedy of Hamlet, Prince of Denmark.\n\nHamlet, Prince of Denmark.\nHoratio, friend to Hamlet.\n\n"
         "Act I: Elsinore.\n\nScene I: A platform before the castle.\n\n[Enter Hamlet and Horatio]\n\nHamlet:\n "
         "To be, or not to be, that is the question! Whether 'tis nobler in the mind to suffer the slings and "
         "arrows of outrageous fortune.\n\nHoratio:\n My lord, I came to see your father's funeral.\n\n[Exeunt]\n",
         None, "printf %s '<real Hamlet lines laid out as a play: no assignment/output sentences>'"),
    ]
    for name, codec, prog, plain, gen in cases:
        got, err = (chef_oracle if codec == "chef" else spl_oracle)(prog)
        decoy = plain is None and name.split("-")[1] == "decoy"
        if not decoy:
            assert got is not None, (name, err)
            if plain is not None:
                assert got == plain, (name, got)
        else:
            assert not got or not got.strip() or err, (name, got)
        fx = {"codec": codec, "plain": None if decoy else got, "encoded": prog, "generator_cmd": gen,
              "oracle_cmd": CHEF_ORACLE if codec == "chef" else SPL_ORACLE,
              "oracle_plain": got if got is not None else "", "oracle_error": err}
        if decoy:
            fx.update(decoy=True, expected="none")
        else:
            fx["expected"] = got
        (HERE / f"{name}.json").write_text(json.dumps(fx, indent=1, ensure_ascii=False) + "\n")
        out.append((name, repr((got or err)[:70])))
    for o in out:
        print(*o)


if __name__ == "__main__":
    main()
