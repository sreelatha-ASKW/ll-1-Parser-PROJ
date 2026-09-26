from flask import Flask, render_template, request

app = Flask(__name__)


# -----------------------------
# Parse Grammar
# -----------------------------
def parse_grammar(grammar_text):

    grammar = {}

    lines = grammar_text.strip().splitlines()

    for line in lines:

        if "->" not in line:
            continue

        left, right = line.split("->", 1)

        left = left.strip()

        alternatives = right.split("|")

        grammar[left] = []

        for alternative in alternatives:
            grammar[left].append(alternative.strip())

    return grammar


# -----------------------------
# FIRST
# -----------------------------
def get_first(grammar):

    first = {}

    for non_terminal in grammar:
        first[non_terminal] = set()

    def calculate(symbol, visited=None):

        if visited is None:
            visited = set()

        # Terminal
        if symbol not in grammar:
            return {symbol}

        # Avoid infinite recursion
        if symbol in visited:
            return set()

        visited.add(symbol)

        result = set()

        for production in grammar[symbol]:

            symbols = production.split()

            # Epsilon
            if symbols == ["#"]:
                result.add("#")
                continue

            all_epsilon = True

            for s in symbols:

                temp = calculate(s, visited.copy())

                result.update(temp - {"#"})

                if "#" not in temp:
                    all_epsilon = False
                    break

            if all_epsilon:
                result.add("#")

        return result

    for non_terminal in grammar:
        first[non_terminal] = calculate(non_terminal)

    return first


# -----------------------------
# FOLLOW
# -----------------------------
def get_follow(grammar, first, start_symbol):

    follow = {}

    for non_terminal in grammar:
        follow[non_terminal] = set()

    # Start symbol contains $
    follow[start_symbol].add("$")

    changed = True

    while changed:

        changed = False

        for lhs in grammar:

            for production in grammar[lhs]:

                symbols = production.split()

                for i, symbol in enumerate(symbols):

                    if symbol not in grammar:
                        continue

                    # There is a symbol after current symbol
                    if i + 1 < len(symbols):

                        next_symbol = symbols[i + 1]

                        # Next symbol is non-terminal
                        if next_symbol in grammar:

                            first_next = first[next_symbol]

                            old_size = len(follow[symbol])

                            follow[symbol].update(
                                first_next - {"#"}
                            )

                            if "#" in first_next:
                                follow[symbol].update(
                                    follow[lhs]
                                )

                            if len(follow[symbol]) != old_size:
                                changed = True

                        # Next symbol is terminal
                        else:

                            old_size = len(follow[symbol])

                            follow[symbol].add(next_symbol)

                            if len(follow[symbol]) != old_size:
                                changed = True

                    # Current symbol is at the end
                    else:

                        old_size = len(follow[symbol])

                        follow[symbol].update(
                            follow[lhs]
                        )

                        if len(follow[symbol]) != old_size:
                            changed = True

    return follow


# -----------------------------
# Home Page
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def home():

    first = {}
    follow = {}
    grammar_text = ""

    if request.method == "POST":

        grammar_text = request.form.get("grammar", "")

        grammar = parse_grammar(grammar_text)

        if grammar:

            # FIRST
            first = get_first(grammar)

            # First non-terminal is start symbol
            start_symbol = list(grammar.keys())[0]

            # FOLLOW
            follow = get_follow(
                grammar,
                first,
                start_symbol
            )

    return render_template(
        "index.html",
        first=first,
        follow=follow,
        grammar_text=grammar_text
    )


# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)