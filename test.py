from ExpertSystem import ExpertSystem

es = ExpertSystem()

es.add_rule("A | E => F")
es.add_rule("A | B => E")
es.add_rule("A | B => !E")
es.add_rule("A + !B => G")
# es.add_rule("A => G")
# es.add_rule("A + (!B + C) + A => D")
# es.add_rule("C => E")

es.add_fact("A")
query = "F"


es.solve(query)
