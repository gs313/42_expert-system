from ExpertSystem import ExpertSystem

es = ExpertSystem()

es.add_rule(" E => F ^ G")
es.add_rule("A + B => E")
es.add_rule("A => G")
# es.add_rule("A + (!B + C) + A => D")
# es.add_rule("C => E")

es.add_fact("AB")
query = "F"

is_true = es.solve(query)
print(is_true)
if is_true == None:
    print(f"ผลลัพธ์ของ {query} คือ: สรุปไม่ได้")
else:
    print(f"ผลลัพธ์ของ {query} คือ: {'จริง (True)' if is_true else 'เท็จ'}")