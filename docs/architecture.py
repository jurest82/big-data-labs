"""Generates the diagram of each lab: the architecture of the AWS labs and the
data model of labs 1A and 1B.

Each diagram comes in two sizes: the full one, with details and labels on the
arrows, for the lab README and the slides, and a small one (`*_small.png`),
with only the icons and their names, for the root README.
"""
# pylint: disable=expression-not-assigned

import graphviz
from diagrams import Diagram, Edge
from diagrams.aws.analytics import (Athena, Glue, GlueCrawlers, GlueDataCatalog,
                                    KinesisDataFirehose)
from diagrams.aws.storage import S3
from diagrams.onprem.client import Client

DARK = "#1a1a1a"
GREY = "#5c5c5c"

FULL = {
    "node_h": "3.9",
    "graph": {
        "fontsize": "34",
        "fontcolor": DARK,
        "splines": "spline",
        "nodesep": "1.2",
        "ranksep": "1.5",
        "pad": "1.2",
        "dpi": "144",
    },
    "node": {
        "fontsize": "21",
        "fontcolor": DARK
    },
    "edge_font": "17",
    "edge_width": "2.4",
}

SMALL = {
    "node_h": "2.4",
    "graph": {
        "fontsize": "44",
        "fontcolor": DARK,
        "splines": "spline",
        "nodesep": "0.7",
        "ranksep": "1.7",
        "pad": "0.9",
        "dpi": "144",
    },
    "node": {
        "fontsize": "30",
        "fontcolor": DARK
    },
    "edge_font": "17",
    "edge_width": "3.2",
}


class Kit:
    """The sizes, labels and edge styles of one diagram size."""

    def __init__(self, small):
        self.small = small
        self.cfg = SMALL if small else FULL
        self.height = self.cfg["node_h"]

    def pick(self, full, short):
        """A node label: the detailed one, or the short name."""
        return short if self.small else full

    def note(self, text):
        """An arrow label: the full diagram has them, the small one does not."""
        return "" if self.small else text

    def diagram(self, title, short_title, filename):
        suffix = "_small" if self.small else ""
        return Diagram(self.pick(title, short_title),
                       filename=filename + suffix,
                       show=False,
                       direction="LR",
                       graph_attr=self.cfg["graph"],
                       node_attr=self.cfg["node"])

    def edge(self, **kwargs):
        return Edge(color=DARK,
                    penwidth=self.cfg["edge_width"],
                    fontcolor=DARK,
                    fontsize=self.cfg["edge_font"],
                    **kwargs)

    def flow(self, **kwargs):
        """Main data flow. High weight so the chain stays a horizontal line."""
        return self.edge(weight="200", **kwargs)

    def loose(self, **kwargs):
        """Edge whose target is already ranked by another edge: it does not
        pull its endpoints off their row."""
        return self.edge(constraint="false", weight="0", **kwargs)

    def branch(self, **kwargs):
        """Hangs a side node off the chain with a low weight, so it does not
        compete with the chain for its row."""
        return self.edge(style="dashed", weight="1", **kwargs)

    def support(self, **kwargs):
        """Metadata lookup, not data flow: dashed and grey."""
        return Edge(color=GREY,
                    penwidth="1.8" if not self.small else "2.6",
                    fontcolor=GREY,
                    fontsize=self.cfg["edge_font"],
                    style="dashed",
                    **kwargs)


def lab02(kit):
    with kit.diagram("Lab 2 - A data lake with S3, Glue and Athena", "Lab 2",
                     "lab02_data_lake"):
        # Declared first so it ranks above the chain: its arrows then reach
        # the icons from above, away from their names.
        athena = Athena("Athena", height=kit.height, labelloc="t")
        files = Client(kit.pick("Your computer\n(generated files)",
                                "Your computer"),
                       height=kit.height)
        lake = S3(kit.pick("S3 lake\nraw/ zone", "S3 lake"), height=kit.height)
        crawler = GlueCrawlers("Glue crawler", height=kit.height)
        catalog = GlueDataCatalog(kit.pick("Glue catalog\norders, reviews",
                                           "Glue catalog"),
                                  height=kit.height)

        files >> kit.flow(label=kit.note("aws s3 sync")) >> lake
        lake >> kit.flow(
            label=kit.note("reads orders/\nand reviews/")) >> crawler
        crawler >> kit.flow(label=kit.note("writes the\ntables")) >> catalog
        athena >> kit.support(
            label=kit.note("table  \ndefinition  ")) >> catalog
        athena >> kit.loose(label=kit.note("reads  \nthe files  "),
                            style="dashed") >> lake


def lab03(kit):
    with kit.diagram("Lab 3 - An Apache Iceberg table in Athena", "Lab 3",
                     "lab03_iceberg"):
        csv = S3(kit.pick("S3 lake\nraw/orders/\nCSV, 32 MiB", "S3 CSV"),
                 height=kit.height)
        athena = Athena("Athena", height=kit.height)
        iceberg = S3(kit.pick("S3 lake\niceberg/orders/\nParquet + metadata",
                              "S3 Iceberg"),
                     height=kit.height)
        catalog = GlueDataCatalog(kit.pick(
            "Glue catalog\norders, "
            "orders_iceberg", "Glue catalog"),
                                  height=kit.height)

        csv >> kit.flow(label=kit.note("reads the table\norders")) >> athena
        athena >> kit.flow(
            label=kit.note("CREATE TABLE AS SELECT\nUPDATE, ALTER")) >> iceberg
        athena >> kit.support(label=kit.note("table\ndefinition")) >> catalog


def lab04(kit):
    with kit.diagram(
            "Lab 4 - Medallion layers in one S3 bucket, with SQL in "
            "Athena", "Lab 4", "lab04_medallion"):
        # Declared first so it ranks above the chain, away from the labels.
        rejected = S3(kit.pick(
            "Rejected rows\nsilver/orders_rejected/\nIceberg, 8328 lines",
            "Rejected rows"),
                      height=kit.height,
                      labelloc="t")
        bronze = S3(kit.pick("Bronze\nraw/orders_october/\nCSV, 96496 lines",
                             "Bronze"),
                    height=kit.height)
        quality = Athena(kit.pick("Athena\nquality rules", "Athena"),
                         height=kit.height)
        silver = S3(kit.pick("Silver\nsilver/orders/\nIceberg, 88168 lines",
                             "Silver"),
                    height=kit.height)
        aggregate = Athena(kit.pick("Athena\nsales by category\nand month",
                                    "Athena"),
                           height=kit.height)
        gold = S3(kit.pick("Gold\ngold/\nIceberg, 3 rows", "Gold"),
                  height=kit.height)

        bronze >> kit.flow(label=kit.note("reads")) >> quality
        quality >> kit.flow(label=kit.note("valid rows")) >> silver
        silver >> kit.flow(label=kit.note("reads")) >> aggregate
        aggregate >> kit.flow(label=kit.note("writes")) >> gold
        quality >> kit.branch() >> rejected


def lab05(kit):
    with kit.diagram("Lab 5 - Click events to S3 with Firehose", "Lab 5",
                     "lab05_firehose"):
        producer = Client(kit.pick("Your computer\nsend_clicks.py",
                                   "Your computer"),
                          height=kit.height)
        firehose = KinesisDataFirehose("Firehose", height=kit.height)
        bucket = S3(kit.pick("S3\nclicks/yyyy/MM/dd/HH/", "S3"),
                    height=kit.height)
        athena = Athena("Athena", height=kit.height)
        catalog = Glue(kit.pick("Glue\ntable clicks", "Glue"),
                       height=kit.height)

        producer >> kit.flow(
            label=kit.note("PutRecordBatch\n500 clicks max")) >> firehose
        firehose >> kit.flow(
            label=kit.note("a file every\n60 s or 5 MiB")) >> bucket
        bucket << kit.flow(label=kit.note("reads\nthe files")) << athena
        athena >> kit.support(label=kit.note("table\ndefinition")) >> catalog


BLUE = "#336791"
AMBER = "#b45309"
TEAL = "#0f766e"


def model_table(name, rows, color, note=""):
    """The HTML label of a table: a colored header, one row per column and
    an optional note at the bottom."""
    cells = ""
    for col, tag in rows:
        cells += ('<TR><TD ALIGN="LEFT">' + col + '</TD><TD>' + tag +
                  '</TD></TR>')
    if note:
        cells += ('<TR><TD COLSPAN="2" ALIGN="LEFT"><I>' + note +
                  '</I></TD></TR>')
    return ('<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" '
            'CELLPADDING="7"><TR><TD BGCOLOR="' + color +
            '" COLSPAN="2"><FONT COLOR="white"><B>' + name +
            '</B></FONT></TD></TR>' + cells + '</TABLE>>')


def model_node(graph, kit, name, rows, color, **attrs):
    """A table of a data model: all its columns, or just a named box."""
    note = attrs.pop("note", "")
    if kit.small:
        graph.node(name,
                   label=name,
                   shape="box",
                   style="filled,rounded",
                   fillcolor=color,
                   fontcolor="white",
                   margin="0.35,0.2",
                   **attrs)
    else:
        graph.node(name,
                   label=model_table(name, rows, color, note),
                   shape="plain",
                   **attrs)


def model_graph(kit, engine, title, short_title, **graph_attr):
    """A data model graph with the look of the architecture diagrams."""
    return graphviz.Digraph(engine=engine,
                            graph_attr={
                                "label": kit.pick(title, short_title),
                                "labelloc": "b",
                                "fontname": "Sans-Serif",
                                "fontsize": "34" if not kit.small else "44",
                                "fontcolor": DARK,
                                "pad": "0.9",
                                "dpi": "144",
                                **graph_attr
                            },
                            node_attr={
                                "fontname": "Sans-Serif",
                                "fontsize": "20" if not kit.small else "30",
                                "fontcolor": DARK
                            },
                            edge_attr={
                                "color": DARK,
                                "penwidth": "2.4" if not kit.small else "3.2",
                                "fontname": "Sans-Serif",
                                "fontsize": "17",
                                "fontcolor": DARK
                            })


def lab01a(kit):
    graph = model_graph(
        kit,
        "dot",
        "Lab 1A - From one flat table to four tables, in local PostgreSQL",
        "Lab 1A",
        rankdir="LR",
        compound="true",
        nodesep="0.9",
        ranksep="1.4")
    model_node(graph, kit, "flat_orders", [
        ("order_id", ""),
        ("order_date", ""),
        ("customer_name", ""),
        ("customer_address", ""),
        ("product_name", ""),
        ("quantity", ""),
        ("amount", ""),
    ], GREY)
    # The flat table has no categories or prices: the products come from a
    # catalog typed in the script.
    graph.node(
        "catalog",
        label=kit.pick(
            "Product catalog\n(typed in the script,\nwith category and price)",
            "Product catalog"),
        shape="box",
        style="dashed,rounded",
        margin="0.3,0.2")
    with graph.subgraph(name="cluster_tables") as tables:
        tables.attr(label="",
                    style="rounded,dashed",
                    color=GREY,
                    penwidth="2.4")
        model_node(tables, kit, "customers",
                   [("customer_id", "PK"), ("name", ""), ("address", "")], BLUE)
        model_node(tables, kit, "products", [("product_id", "PK"), ("name", ""),
                                             ("category", ""), ("price", "")],
                   BLUE)
        model_node(tables, kit, "orders", [("order_id", "PK"),
                                           ("customer_id", "FK"),
                                           ("order_date", "")], BLUE)
        model_node(tables, kit, "order_items", [("order_id", "PK, FK"),
                                                ("product_id", "PK, FK"),
                                                ("quantity", "")], BLUE)
    graph.edge("flat_orders",
               "order_items",
               lhead="cluster_tables",
               label=kit.note("copies customers,\norders and order_items"))
    graph.edge("catalog", "products", style="dashed")
    for source, target in (("order_items", "orders"),
                           ("order_items", "products"), ("orders",
                                                         "customers")):
        graph.edge(source, target, color=GREY, style="dashed")
    graph.render(filename="lab01a_normalization" +
                 ("_small" if kit.small else ""),
                 format="png",
                 cleanup=True)


def lab01b(kit):
    graph = model_graph(
        kit,
        "neato",
        "Lab 1B - A star schema and a data mart, in local PostgreSQL",
        "Lab 1B",
        splines="true")
    if kit.small:
        spots = {
            "oltp": (-9.0, 0),
            "fact": (0, 0),
            "product": (-3.5, 1.5),
            "date": (3.5, 1.5),
            "customer": (-3.5, -1.5),
            "city": (3.5, -1.5),
            "mart": (9.7, 0),
            "star": (0, 0, 11.6, 4.8)
        }
    else:
        spots = {
            "oltp": (-8.6, 0),
            "fact": (0, 0),
            "product": (-3.6, 2.3),
            "date": (3.6, 2.3),
            "customer": (-3.6, -2.3),
            "city": (3.6, -2.3),
            "mart": (9.4, 0),
            "star": (0, 0.15, 10.8, 8.2)
        }

    def at(key):
        return {
            "pos": f"{spots[key][0]},{spots[key][1]}!"
        }

    # The frame of the star schema, drawn first so the tables sit on top.
    graph.node("star",
               label=kit.pick("schema lab_01b", ""),
               shape="box",
               style="rounded,dashed",
               color=GREY,
               penwidth="2.4",
               fixedsize="true",
               width=str(spots["star"][2]),
               height=str(spots["star"][3]),
               labelloc="b",
               fontcolor=GREY,
               **at("star"))
    model_node(graph, kit, "lab_01b_oltp", [("customers", ""), ("products", ""),
                                            ("orders", ""),
                                            ("order_items", "")], GREY,
               **at("oltp"))
    model_node(graph, kit, "fact_sales", [("date_id", "FK"),
                                          ("product_id", "FK"),
                                          ("customer_id", "FK"),
                                          ("city_id", "FK"), ("quantity", ""),
                                          ("amount", "")], AMBER, **at("fact"))
    model_node(graph, kit, "dim_product", [("product_id", "PK"), ("name", ""),
                                           ("category", ""), ("price", "")],
               BLUE, **at("product"))
    model_node(graph, kit, "dim_date", [("date_id", "PK"), ("full_date", ""),
                                        ("year", ""), ("month", ""),
                                        ("month_name", "")], BLUE, **at("date"))
    model_node(graph, kit, "dim_customer", [("customer_id", "PK"), ("name", ""),
                                            ("address", "")], BLUE,
               **at("customer"))
    model_node(graph, kit, "dim_city", [("city_id", "PK"), ("name", "")], BLUE,
               **at("city"))
    model_node(graph,
               kit,
               "mart_marketing_sales (view)", [("category", ""), ("city", ""),
                                               ("units", ""), ("sales", "")],
               TEAL,
               note=('reads fact_sales,<BR ALIGN="LEFT"/>'
                     'dim_product and dim_city<BR ALIGN="LEFT"/>'),
               **at("mart"))
    graph.edge("lab_01b_oltp", "star", label=kit.note("load"))
    for dim in ("dim_product", "dim_date", "dim_customer", "dim_city"):
        graph.edge("fact_sales", dim, color=GREY, style="dashed")
    graph.edge("star", "mart_marketing_sales (view)")
    graph.render(filename="lab01b_star_schema" +
                 ("_small" if kit.small else ""),
                 format="png",
                 cleanup=True)


for is_small in (False, True):
    lab_kit = Kit(is_small)
    for lab in (lab01a, lab01b, lab02, lab03, lab04, lab05):
        lab(lab_kit)
