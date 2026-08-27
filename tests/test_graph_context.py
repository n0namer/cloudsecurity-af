from __future__ import annotations

import json
from pathlib import Path

from cloudsecurity_af.agents._utils import build_graph_context_for_hunter


def _write_inputs(tmp_path: Path) -> tuple[str, str]:
    graph = {
        "nodes": [
            {
                "resource_id": "aws_iam_role.admin",
                "resource_type": "aws_iam_role",
                "file_path": "iam.tf",
                "config_summary": "AdministratorAccess policy attached",
            },
            {
                "resource_id": "aws_s3_bucket.data",
                "resource_type": "aws_s3_bucket",
                "file_path": "storage.tf",
                "config_summary": "Public access enabled, no encryption",
            },
            {
                "resource_id": "aws_vpc.main",
                "resource_type": "aws_vpc",
                "file_path": "network.tf",
                "config_summary": "10.0.0.0/16 CIDR",
            },
        ],
        "edges": [
            {
                "source": "aws_iam_role.admin",
                "target": "aws_s3_bucket.data",
                "type": "data_access",
                "description": "Admin role can read data bucket",
            },
            {
                "source": "aws_vpc.main",
                "target": "aws_s3_bucket.data",
                "type": "network_path",
                "description": "VPC endpoint to S3",
            },
        ],
        "clusters": [],
    }
    inventory = {
        "resources": [
            {"id": "aws_iam_role.admin", "provider": "aws"},
            {"id": "aws_s3_bucket.data", "provider": "aws"},
            {"id": "aws_vpc.main", "provider": "aws"},
        ],
        "modules": [],
        "variables": [],
        "outputs": [],
        "provider_configs": [],
    }
    graph_path = tmp_path / "graph.json"
    inventory_path = tmp_path / "inventory.json"
    graph_path.write_text(json.dumps(graph))
    inventory_path.write_text(json.dumps(inventory))
    return str(graph_path), str(inventory_path)


class TestBuildGraphContextForHunter:
    def test_iam_keywords_filter(self, tmp_path: Path) -> None:
        graph_path, inventory_path = _write_inputs(tmp_path)
        summary, _, edges = build_graph_context_for_hunter(graph_path, inventory_path, ["iam", "role"])
        assert "aws_iam_role.admin" in summary
        # One-hop connected resources are intentionally included for hunter context.
        assert "aws_s3_bucket.data" in summary
        assert "aws_iam_role.admin" in edges

    def test_network_keywords_filter(self, tmp_path: Path) -> None:
        graph_path, inventory_path = _write_inputs(tmp_path)
        summary, _, _ = build_graph_context_for_hunter(graph_path, inventory_path, ["vpc", "subnet"])
        assert "aws_vpc.main" in summary
        assert "aws_iam_role.admin" not in summary

    def test_s3_keywords_return_bucket(self, tmp_path: Path) -> None:
        graph_path, inventory_path = _write_inputs(tmp_path)
        summary, _, _ = build_graph_context_for_hunter(graph_path, inventory_path, ["s3", "bucket"])
        assert "aws_s3_bucket.data" in summary

    def test_empty_keyword_matches_all(self, tmp_path: Path) -> None:
        graph_path, inventory_path = _write_inputs(tmp_path)
        summary, _, _ = build_graph_context_for_hunter(graph_path, inventory_path, [""])
        assert "aws_iam_role.admin" in summary
        assert "aws_s3_bucket.data" in summary
        assert "aws_vpc.main" in summary

    def test_no_match_returns_none_message(self, tmp_path: Path) -> None:
        graph_path, inventory_path = _write_inputs(tmp_path)
        summary, _, _ = build_graph_context_for_hunter(graph_path, inventory_path, ["nonexistent_type_xyz"])
        assert "none matched" in summary

    def test_inventory_stats_format(self, tmp_path: Path) -> None:
        graph_path, inventory_path = _write_inputs(tmp_path)
        _, stats, _ = build_graph_context_for_hunter(graph_path, inventory_path, ["iam"])
        assert "Total resources: 3" in stats
        assert "Graph nodes: 3" in stats
        assert "Graph edges: 2" in stats

    def test_edge_includes_connected_edges(self, tmp_path: Path) -> None:
        graph_path, inventory_path = _write_inputs(tmp_path)
        _, _, edges = build_graph_context_for_hunter(graph_path, inventory_path, ["iam", "role"])
        assert "data_access" in edges
        assert "aws_s3_bucket.data" in edges

    def test_config_summary_in_output(self, tmp_path: Path) -> None:
        graph_path, inventory_path = _write_inputs(tmp_path)
        summary, _, _ = build_graph_context_for_hunter(graph_path, inventory_path, ["iam"])
        assert "AdministratorAccess" in summary

    def test_empty_graph(self, tmp_path: Path) -> None:
        graph_path = tmp_path / "empty-graph.json"
        inventory_path = tmp_path / "empty-inventory.json"
        graph_path.write_text(json.dumps({"nodes": [], "edges": [], "clusters": []}))
        inventory_path.write_text(json.dumps({"resources": [], "modules": [], "variables": [], "outputs": []}))
        summary, stats, edges = build_graph_context_for_hunter(str(graph_path), str(inventory_path), ["iam"])
        assert "none matched" in summary
        assert "Total resources: 0" in stats
        assert "no edges matched" in edges
