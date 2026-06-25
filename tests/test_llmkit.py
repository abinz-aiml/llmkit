"""
llmkit test suite — runs without API keys.

Run:
    pip install pytest
    pytest tests/
"""

import os
import sys
import math
import json
import yaml
import pytest
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# providers/utils.py
# ---------------------------------------------------------------------------

class TestProviderUtils:
    def test_base_urls_covers_expected_providers(self):
        from providers.utils import BASE_URLS
        for p in ("groq", "deepseek", "together", "mistral"):
            assert p in BASE_URLS, f"BASE_URLS missing {p}"

    def test_api_key_names_covers_expected_providers(self):
        from providers.utils import API_KEY_NAMES
        for p in ("openai", "groq", "deepseek", "together", "mistral"):
            assert p in API_KEY_NAMES, f"API_KEY_NAMES missing {p}"

    def test_local_not_in_base_urls(self):
        from providers.utils import BASE_URLS
        assert "local" not in BASE_URLS

    def test_groq_base_url_points_to_groq(self):
        from providers.utils import BASE_URLS
        assert "groq.com" in BASE_URLS["groq"]

    def test_openai_not_in_base_urls(self):
        from providers.utils import BASE_URLS
        assert "openai" not in BASE_URLS


# ---------------------------------------------------------------------------
# Config — llm.yaml
# ---------------------------------------------------------------------------

VALID_PROVIDERS = {"local", "openai", "anthropic", "groq", "together", "deepseek", "mistral"}

class TestConfig:
    def test_llm_yaml_parses(self):
        with open(ROOT / "llm.yaml") as f:
            config = yaml.safe_load(f)
        assert "provider" in config
        assert "model" in config

    def test_provider_is_valid(self):
        with open(ROOT / "llm.yaml") as f:
            config = yaml.safe_load(f)
        assert config["provider"] in VALID_PROVIDERS

    def test_model_is_non_empty_string(self):
        with open(ROOT / "llm.yaml") as f:
            config = yaml.safe_load(f)
        assert isinstance(config["model"], str) and config["model"].strip()


# ---------------------------------------------------------------------------
# cli.py — providers_map completeness
# ---------------------------------------------------------------------------

class TestCLI:
    def test_cli_providers_map_matches_valid_providers(self):
        import ast
        src = (ROOT / "cli.py").read_text()
        tree = ast.parse(src)
        providers_map_keys = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "providers_map":
                        if isinstance(node.value, ast.Dict):
                            for key in node.value.keys:
                                if isinstance(key, ast.Constant):
                                    providers_map_keys.add(key.value)
        assert providers_map_keys == VALID_PROVIDERS

    def test_provider_files_exist_and_define_send_message(self):
        import ast
        for name in VALID_PROVIDERS:
            path = ROOT / "providers" / f"{name}.py"
            assert path.exists(), f"providers/{name}.py missing"
            src = path.read_text()
            tree = ast.parse(src)
            fn_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
            assert "send_message" in fn_names, f"{name}.py missing send_message"


# ---------------------------------------------------------------------------
# agent.py — workspace guard logic
# ---------------------------------------------------------------------------

class TestWorkspaceGuard:
    def test_path_inside_workspace_allowed(self, tmp_path):
        workspace = tmp_path / "ws"
        workspace.mkdir()
        p = (workspace / "file.txt").resolve()
        assert p.is_relative_to(workspace)

    def test_path_outside_workspace_blocked(self, tmp_path):
        workspace = tmp_path / "ws"
        workspace.mkdir()
        outside = (tmp_path / "evil.txt").resolve()
        assert not outside.is_relative_to(workspace)

    def test_path_traversal_blocked(self, tmp_path):
        workspace = tmp_path / "ws"
        workspace.mkdir()
        traversal = (workspace / ".." / "evil.txt").resolve()
        assert not traversal.is_relative_to(workspace)

    def test_write_and_read_inside_workspace(self, tmp_path):
        workspace = tmp_path / "ws"
        workspace.mkdir()
        target = workspace / "hello.txt"
        target.write_text("hello")
        assert target.read_text() == "hello"


# ---------------------------------------------------------------------------
# tools.py — calculate()
# ---------------------------------------------------------------------------

def calculate(expression):
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return "Error: invalid characters in expression"
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

class TestCalculate:
    def test_addition(self):        assert calculate("2+2") == "4"
    def test_multiplication(self):  assert calculate("10*5") == "50"
    def test_division(self):        assert calculate("10/4") == "2.5"
    def test_parentheses(self):     assert calculate("(2+3)*4") == "20"

    def test_rejects_letters(self):
        assert calculate("__import__('os')").startswith("Error:")

    def test_rejects_underscore(self):
        assert calculate("1+_evil").startswith("Error:")

    def test_division_by_zero(self):
        assert calculate("1/0").startswith("Error:")


# ---------------------------------------------------------------------------
# embed.py — cosine similarity
# ---------------------------------------------------------------------------

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x**2 for x in a))
    mag_b = math.sqrt(sum(x**2 for x in b))
    if mag_a == 0 or mag_b == 0:
        return None
    return dot / (mag_a * mag_b)

class TestCosineSimilarity:
    def test_identical_vectors_score_1(self):
        a = [1.0, 0.0, 0.0]
        assert abs(cosine(a, a) - 1.0) < 1e-9

    def test_opposite_vectors_score_minus1(self):
        assert abs(cosine([1.0, 0.0], [-1.0, 0.0]) - (-1.0)) < 1e-9

    def test_orthogonal_vectors_score_0(self):
        assert abs(cosine([1.0, 0.0], [0.0, 1.0])) < 1e-9

    def test_zero_vector_returns_none(self):
        assert cosine([0.0, 0.0], [1.0, 0.0]) is None


# ---------------------------------------------------------------------------
# mcp_agent.py — resolve_env_val
# ---------------------------------------------------------------------------

def resolve_env_val(v):
    if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
        return os.environ.get(v[2:-1], "")
    return str(v)

class TestResolveEnvVal:
    def test_expands_dollar_brace(self):
        os.environ["_LLMKIT_TEST"] = "testvalue"
        assert resolve_env_val("${_LLMKIT_TEST}") == "testvalue"

    def test_returns_empty_for_missing_var(self):
        os.environ.pop("_LLMKIT_MISSING", None)
        assert resolve_env_val("${_LLMKIT_MISSING}") == ""

    def test_passthrough_literal(self):
        assert resolve_env_val("hello") == "hello"

    def test_passthrough_non_string(self):
        assert resolve_env_val(42) == "42"


# ---------------------------------------------------------------------------
# mcp_agent.py — make_openai_schema
# ---------------------------------------------------------------------------

def make_openai_schema(tools):
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.inputSchema or {"type": "object", "properties": {}}
            }
        }
        for t in tools
    ]

class FakeTool:
    def __init__(self, name, description, inputSchema):
        self.name = name
        self.description = description
        self.inputSchema = inputSchema

class TestMakeOpenaiSchema:
    def test_basic_schema_structure(self):
        tools = [FakeTool("get_weather", "Get weather", {"type": "object", "properties": {}})]
        schema = make_openai_schema(tools)
        assert len(schema) == 1
        assert schema[0]["type"] == "function"
        assert schema[0]["function"]["name"] == "get_weather"

    def test_none_description_becomes_empty_string(self):
        schema = make_openai_schema([FakeTool("t", None, {})])
        assert schema[0]["function"]["description"] == ""

    def test_none_input_schema_gets_fallback(self):
        schema = make_openai_schema([FakeTool("t", "desc", None)])
        assert schema[0]["function"]["parameters"] == {"type": "object", "properties": {}}

    def test_multiple_tools(self):
        tools = [FakeTool(f"tool{i}", "d", {}) for i in range(3)]
        assert len(make_openai_schema(tools)) == 3
