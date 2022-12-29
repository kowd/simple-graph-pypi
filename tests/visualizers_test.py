from pathlib import Path
from filecmp import cmp
import database as db
from visualizers import graphviz_visualize, graphviz_visualize_bodies
from test_common import database_test_file, nodes, edges, apple


def test_visualization(database_test_file, apple, tmp_path):
    dot_raw = tmp_path / "apple-raw.dot"
    graphviz_visualize(database_test_file, dot_raw, [4, 1, 5])
    here = Path(__file__).parent.resolve()
    assert cmp(dot_raw, here / "fixtures" / "apple-raw.dot")
    dot = tmp_path / "apple.dot"
    graphviz_visualize(database_test_file, dot, [4, 1, 5], exclude_node_keys=[
        'type'], hide_edge_key=True)
    assert cmp(dot, Path.cwd() / ".." / ".examples" / "apple.dot")


def test_visualize_bodies(database_test_file, apple, tmp_path):
    dot_raw = tmp_path / "apple-raw.dot"
    path_with_bodies = db.traverse(database_test_file, 4, 5, with_bodies=True)
    graphviz_visualize_bodies(dot_raw, path_with_bodies)
    here = Path(__file__).parent.resolve()
    assert cmp(dot_raw, here / "fixtures" / "apple-raw.dot")
    dot = tmp_path / "apple.dot"
    graphviz_visualize_bodies(dot, path_with_bodies, exclude_node_keys=[
        'type'], hide_edge_key=True)
    assert cmp(dot, here / "fixtures" / "apple.dot")
