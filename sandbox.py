import pyyed

g = pyyed.Graph()

g.add_node('foo', font_family="Zapfino")
g.add_node('foo2', shape="roundrectangle", font_style="bolditalic",
           underlined_text="true")

g.add_edge_by_id('foo1', 'foo2')
g.add_node('abc', font_size="72", height="100")

b = g.add_node('bar')
b.add_label("Multi\nline\ntext")

f = g.add_node('foobar')
f.add_label("""Multi
Line
Text!""")

g.add_edge_by_id('foo', 'foo1', label="EDGE!", width="3.0", color="#0000FF",
                 arrowhead="white_diamond", arrowfoot="standard", line_type="dotted")

print(g.get_graph())

print("\n\n\n")

g = pyyed.Graph()
n1 = g.add_node('foo', font_family="Zapfino")

grp1 = g.add_group("MY_Group", shape="diamond")
n2 = grp1.add_node('foo2', shape="roundrectangle", font_style="bolditalic",
            underlined_text="true")
n3 = grp1.add_node('abc', font_size="72", height="100")

g.add_edge(n2, n3)
g.add_edge(n1, grp1)

g.write_graph("test.graphml")

print(g.get_graph())
