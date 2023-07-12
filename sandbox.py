import pyyed

g = pyyed.Graph()

n1 = g.add_node('foo', font_family="Zapfino")
n2 = g.add_node('foo2', shape="roundrectangle", font_style="bolditalic",
           underlined_text="true")

e1 = g.add_edge(n1, n2)
n3 = g.add_node('abc', font_size="72", height="100")

b = g.add_node('bar')

f = g.add_node('foobar')


e2 = g.add_edge(n2, n3, label="EDGE!", width="3.0", color="#0000FF",
                 arrowhead="white_diamond", arrowfoot="standard", line_type="dotted")

grp1 = g.add_group("MY_Group", shape="diamond")
n4 = grp1.add_node('foo4', shape="roundrectangle", font_style="bolditalic",
            underlined_text="true")
n5 = grp1.add_node('abc2', font_size="72", height="100")

g.add_edge(n4, n5)
g.add_edge(n2, grp1)

print(g.existing_entities)

for (idx, n) in g.existing_entities.items():
    if idx != "G":
        print(f"{idx}: {n.name}")

g.write_graph("test.graphml")
