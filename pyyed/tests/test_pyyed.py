import pyyed
import pyyed.node as pn
import xml.etree.ElementTree as xml

import pytest


def test_graph_added_node_has_default_fill():
    g = pyyed.Graph()
    node = g.add_node(pn.ShapeNode, 'N1')
    assert "#ffffff" == g.nodes[node.id].background


def test_graph_added_node_keeps_custom_fill():
    g = pyyed.Graph()
    node = g.add_node(pn.ShapeNode, 'N1', background="#99CC00")
    assert "#99CC00" == g.nodes[node.id].background


def test_node_properties_after_nodes_and_edges_added():

    g = pyyed.Graph()

    node1 = g.add_node(pn.ShapeNode, 'foo',  shape="ellipse")
    node2  = g.add_node(pn.ShapeNode, 'foo2', shape="roundrectangle", font_style="bolditalic")

    edge1 = g.add_edge(node1, node2)
    node3 = g.add_node(pn.ShapeNode, 'abc', shape="triangle", font_style="bold")

    assert g.nodes[node1.id].shape == "ellipse"
    assert g.nodes[node1.id].list_of_labels[0]._params['fontStyle'] == "plain"

    assert g.nodes[node2.id].shape == "roundrectangle"
    assert g.nodes[node2.id].list_of_labels[0]._params['fontStyle'] == "bolditalic"

    assert g.nodes[node3.id].shape == "triangle"
    assert g.nodes[node3.id].list_of_labels[0]._params['fontStyle'] == "bold"


def test_uml_node_properties_are_set():
    g = pyyed.Graph()

    expected_attributes = "int foo\nString bar"
    expected_methods = "foo()\nbar()"
    expected_stereotype = "abstract"

    node = g.add_node(pn.UmlNode, 'AbstractClass', stereotype=expected_stereotype, attributes=expected_attributes,
                      methods=expected_methods)

    assert g.nodes[node.id].stereotype == expected_stereotype
    assert g.nodes[node.id].attributes == expected_attributes
    assert g.nodes[node.id].methods == expected_methods

    graphml = g.get_graph()
    assertUmlNode(graphml, expected_stereotype,
                  expected_attributes, expected_methods)


def test_uml_stereotype_is_optional():
    g = pyyed.Graph()

    expected_attributes = "int foo\nString bar"
    expected_methods = "foo()\nbar()"

    node = g.add_node(pn.UmlNode, 'Class', attributes=expected_attributes, methods=expected_methods)

    assert g.nodes[node.id].methods == expected_methods
    assert g.nodes[node.id].attributes == expected_attributes

    graphml = g.get_graph()
    assertUmlNode(graphml, "", expected_attributes, expected_methods)


def assertUmlNode(graphml, expected_stereotype, expected_attributes, expected_methods):
    doc = xml.fromstring(graphml)
    nsmap = {'g': 'http://graphml.graphdrawing.org/xmlns',
             'y': 'http://www.yworks.com/xml/graphml'
             }
    umlnode = doc.find(
        'g:graph/g:node/g:data/y:UMLClassNode/y:UML', namespaces=nsmap)
    attributes = umlnode.find('y:AttributeLabel', namespaces=nsmap)
    methods = umlnode.find('y:MethodLabel', namespaces=nsmap)

    assert umlnode.attrib['stereotype'] == expected_stereotype
    assert attributes.text == expected_attributes
    assert methods.text == expected_methods


def test_multiple_edges():
    g = pyyed.Graph()
    nodea = g.add_node(pn.ShapeNode, 'a', font_family="Zapfino").add_label("a2")
    nodeb = g.add_node(pn.ShapeNode, 'b', font_family="Zapfino").add_label("b2")
    nodec = g.add_node(pn.ShapeNode, 'c', font_family="Zapfino").add_label("c2")

    edge1 = g.add_edge(nodea, nodeb)
    edge2 = g.add_edge(nodea, nodeb)
    edge3 = g.add_edge(nodea, nodec)

    e1 = g.edges[edge1.id]
    e2 = g.edges[edge2.id]
    e3 = g.edges[edge3.id]

    assert g.nodes[e1.node1.id].list_of_labels[0]._text == "a"
    assert g.nodes[e1.node2.id].list_of_labels[0]._text == "b"

    assert g.nodes[e2.node1.id].list_of_labels[0]._text == "a"
    assert g.nodes[e2.node2.id].list_of_labels[0]._text == "b"

    assert g.nodes[e3.node1.id].list_of_labels[0]._text == "a"
    assert g.nodes[e3.node2.id].list_of_labels[0]._text == "c"

    # Test-cases for the second label
    assert g.nodes[e1.node1.id].list_of_labels[1]._text == "a2"
    assert g.nodes[e1.node2.id].list_of_labels[1]._text == "b2"

    assert g.nodes[e2.node1.id].list_of_labels[1]._text == "a2"
    assert g.nodes[e2.node2.id].list_of_labels[1]._text == "b2"

    assert g.nodes[e3.node1.id].list_of_labels[1]._text == "a2"
    assert g.nodes[e3.node2.id].list_of_labels[1]._text == "c2"

    assert g.get_graph()


def test_nested_graph_edges():
    g = pyyed.Graph()

    nodea = g.add_node(pn.ShapeNode, "a")
    nodeb = g.add_node(pn.ShapeNode, "b")

    edge1 = g.add_edge(nodea, nodeb)
    g1 = g.add_group('g1')
    g1n1 = g1.add_node(pn.ShapeNode, 'g1n1')
    g1n2 = g1.add_node(pn.ShapeNode, 'g1n2')
    g2 = g1.add_group('g2')
    g2n1 = g2.add_node(pn.ShapeNode, 'g2n1')
    g2n2 = g2.add_node(pn.ShapeNode, 'g2n2')
    g3 = g1.add_group('g3')
    g3n1 = g3.add_node(pn.ShapeNode, 'g3n1')
    g3n2 = g3.add_node(pn.ShapeNode, 'g3n2')

    g1.add_edge(g1n1, g1n2)
    g2.add_edge(g2n2, g2n2)  # No, that's not a typo

    g.add_edge(g2n1, g2n2)
    g1.add_edge(g2n1, g2n2)
    g2.add_edge(g2n1, g2n2)
    with pytest.raises(RuntimeWarning):
        g3.add_edge(g2n1, g2n2)

    with pytest.raises(RuntimeWarning):
        g2.add_edge(nodea, nodeb)

    g.add_edge(g1n1, g2n2)
    g1.add_edge(g1n1, g2n2)
    with pytest.raises(RuntimeWarning):
        g2.add_edge(g1n1, g2n2)
    with pytest.raises(RuntimeWarning):
        g3.add_edge(g1n1, g2n2)
