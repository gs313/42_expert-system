from ExpertSystem import ExpertSystem

es = ExpertSystem()

es.add_rule("A + B => C")
es.add_rule("A + (!B + C) + A => D")
es.add_rule("C => E")
es.add_fact("AB")
query = "D"

is_true = es.solve(query)
print(f"ผลลัพธ์ของ {query} คือ: {'จริง (True)' if is_true else 'เท็จหรือสรุปไม่ได้'}")