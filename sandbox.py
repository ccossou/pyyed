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
g.add_node('foo', font_family="Zapfino")

gg = g.add_group("MY_Group", shape="diamond")
gg.add_node('foo2', shape="roundrectangle", font_style="bolditalic",
            underlined_text="true")
gg.add_node('abc', font_size="72", height="100")

g.add_edge_by_id('foo2', 'abc')
g.add_edge_by_id('foo', 'MY_Group')

print(g.get_graph())
