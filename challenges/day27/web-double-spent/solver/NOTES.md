
## Proposed lib additions
- lib/web/__init__.py candidates(): when GET secondary_route says `credit_not_overspent` (race/double-spend kit), run day27_web_double_spent ALONE first -- any sequential POST to feature_route by default/D12/D13/D19 spends the one credit and burns the target (D27 single: credits already 0 at first contact).
