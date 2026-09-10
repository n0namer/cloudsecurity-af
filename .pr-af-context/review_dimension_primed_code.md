### tests/test_config.py
```
1: from __future__ import annotations
2: 
3: import pytest
4: 
5: from cloudsecurity_af.config import (
6:     DEPTH_CHAIN_LIMITS,
7:     DEPTH_HUNTER_MAP,
8:     DEPTH_PROVER_CAPS,
9:     AIIntegrationConfig,
10:     BudgetConfig,
11:     DepthProfile,
12:     ScanConfig,
13: )
14: from cloudsecurity_af.schemas.input import CloudSecurityInput
15: 
16: 
17: def test_aforge_exec_is_the_default_harness(monkeypatch: pytest.MonkeyPatch) -> None:
18:     for key in (
19:         "CLOUDSECURITY_PROVIDER",
20:         "HARNESS_PROVIDER",
21:         "CLOUDSECURITY_AFORGE_BIN",
22:         "AFORGE_BIN",
23:         "AGENTFIELD_AFORGE_COMMAND",
24:     ):
25:         monkeypatch.delenv(key, raising=False)
26: 
27:     config = AIIntegrationConfig.from_env()
28: 
29:     assert config.provider == "aforge"
30:     assert config.aforge_bin == "aforge"
31:     assert config.provider_env()["AGENTFIELD_AFORGE_COMMAND"] == "exec"
32: 
33: 
34: def test_opencode_remains_an_explicit_rollback(monkeypatch: pytest.MonkeyPatch) -> None:
35:     monkeypatch.setenv("HARNESS_PROVIDER", "opencode")
36: 
37:     assert AIIntegrationConfig.from_env().provider == "opencode"
38: 
39: 
40: def test_aforge_bin_is_overridable(monkeypatch: pytest.MonkeyPatch) -> None:
41:     monkeypatch.delenv("CLOUDSECURITY_AFORGE_BIN", raising=False)
42:     monkeypatch.setenv("AFORGE_BIN", "/opt/aforge/bin/aforge")
43: 
44:     assert AIIntegrationConfig.from_env().aforge_bin == "/opt/aforge/bin/aforge"
45: 
46:     monkeypatch.setenv("CLOUDSECURITY_AFORGE_BIN", "/usr/local/bin/aforge")
47: 
48:     assert AIIntegrationConfig.from_env().aforge_bin == "/usr/local/bin/aforge"
49: 
50: 
51: def test_installed_sdk_supports_the_aforge_harness(monkeypatch: pytest.MonkeyPatch) -> None:
52:     """The pinned agentfield floor must accept the provider/bin this agent wires up."""
53:     from agentfield import HarnessConfig
54: 
55:     for key in ("CLOUDSECURITY_PROVIDER", "HARNESS_PROVIDER", "CLOUDSECURITY_AFORGE_BIN", "AFORGE_BIN"):
56:         monkeypatch.delenv(key, raising=False)
57:     config = AIIntegrationConfig.from_env()
58: 
59:     harness = HarnessConfig(
60:         provider=config.provider,
61:         model=config.harness_model,
62:         max_turns=config.max_turns,
63:         env=config.provider_env(),
64:         opencode_bin=config.opencode_bin,
65:         aforge_bin=config.aforge_bin,
66:         permission_mode="auto",
67:     )
68: 
69:     assert harness.provider == "aforge"
70:     assert harness.aforge_bin == "aforge"
71: 
72: 
73: class TestDepthProfile:
74:     def test_enum_values(self) -> None:
75:         assert DepthProfile.QUICK.value == "quick"
76:         assert DepthProfile.STANDARD.value == "standard"
77:         assert DepthProfile.THOROUGH.value == "thorough"
78: 
79:     def test_quick_hunters(self) -> None:
80:         hunters = DEPTH_HUNTER_MAP[DepthProfile.QUICK]
81:         assert "iam" in hunters
82:         assert "network" in hunters
83:         assert "compliance" not in hunters
84: 
85:     def test_standard_hunters(self) -> None:
86:         hunters = DEPTH_HUNTER_MAP[DepthProfile.STANDARD]
87:         assert len(hunters) == 7
88:         assert "compliance" in hunters
89: 
90:     def test_chain_limits(self) -> None:
91:         assert DEPTH_CHAIN_LIMITS[DepthProfile.QUICK] == 5
92:         assert DEPTH_CHAIN_LIMITS[DepthProfile.STANDARD] == 15
93:         assert DEPTH_CHAIN_LIMITS[DepthProfile.THOROUGH] == 100
94: 
95:     def test_prover_caps(self) -> None:
96:         assert DEPTH_PROVER_CAPS[DepthProfile.QUICK] == 20
97:         assert DEPTH_PROVER_CAPS[DepthProfile.STANDARD] == 30
98:         assert DEPTH_PROVER_CAPS[DepthProfile.THOROUGH] == 10_000
99: 
100: 
101: class TestBudgetConfig:
102:     def test_defaults(self) -> None:
103:         budget = BudgetConfig()
104:         assert budget.max_concurrent_hunters == 4
105:         assert budget.max_concurrent_provers == 3
106:         assert budget.max_cost_usd is None
107:         total = (
108:             budget.recon_budget_pct
109:             + budget.hunt_budget_pct
110:             + budget.chain_budget_pct
111:             + budget.prove_budget_pct
112:             + budget.remediate_budget_pct
113:         )
114:         assert total == pytest.approx(1.0)
115: 
116: 
117: class TestScanConfig:
118:     def test_from_input_tier1(self) -> None:
119:         inp = CloudSecurityInput(repo_url="/tmp/repo", depth="quick")
120:         cfg = ScanConfig.from_input(inp, "/tmp/repo")
121:         assert cfg.depth == DepthProfile.QUICK
122:         assert cfg.tier == 1
123:         assert cfg.repo_path == "/tmp/repo"
124: 
125:     def test_from_input_tier2(self) -> None:
126:         from cloudsecurity_af.schemas.input import CloudConfig
127: 
128:         inp = CloudSecurityInput(repo_url="/tmp/repo", cloud=CloudConfig())
129:         cfg = ScanConfig.from_input(inp, "/tmp/repo")
130:         assert cfg.tier == 2
131: 
132:     def test_from_input_budget_override(self) -> None:
133:         inp = CloudSecurityInput(
134:             repo_url="/tmp/repo",
135:             max_concurrent_hunters=2,
136:             max_concurrent_provers=1,
137:             max_cost_usd=5.0,
138:         )
139:         cfg = ScanConfig.from_input(inp, "/tmp/repo")
140:         assert cfg.budget.max_concurrent_hunters == 2
141:         assert cfg.budget.max_concurrent_provers == 1
142:         assert cfg.budget.max_cost_usd == 5.0
```
_import/usage context:_ IMPORTS: from __future__ import annotations, import pytest, from cloudsecurity_af.config import (, from cloudsecurity_af.schemas.input import CloudSecurityInput, from agentfield import HarnessConfig, from cloudsecurity_af.schemas.input import CloudConfig
IMPORTED BY: none

### src/cloudsecurity_af/config.py
```
1: from __future__ import annotations
2: 
3: import os
4: import tempfile
5: from enum import Enum
6: 
7: from pydantic import BaseModel, Field
8: 
9: from .schemas.input import CloudSecurityInput
10: 
11: 
12: class DepthProfile(str, Enum):
13:     QUICK = "quick"
14:     STANDARD = "standard"
15:     THOROUGH = "thorough"
16: 
17: 
18: class BudgetConfig(BaseModel):
19:     max_cost_usd: float | None = None
20:     max_duration_seconds: int | None = None
21:     max_concurrent_hunters: int = 4
22:     max_concurrent_provers: int = 3
23:     max_concurrent_chain_children: int = 3
24:     recon_budget_pct: float = 0.10
25:     hunt_budget_pct: float = 0.35
26:     chain_budget_pct: float = 0.20
27:     prove_budget_pct: float = 0.25
28:     remediate_budget_pct: float = 0.10
29: 
30: 
31: DEPTH_HUNTER_MAP: dict[DepthProfile, list[str]] = {
32:     DepthProfile.QUICK: ["iam", "network", "data", "secrets", "compute"],
33:     DepthProfile.STANDARD: ["iam", "network", "data", "secrets", "compute", "logging", "compliance"],
34:     DepthProfile.THOROUGH: ["iam", "network", "data", "secrets", "compute", "logging", "compliance"],
35: }
36: 
37: DEPTH_CHAIN_LIMITS: dict[DepthProfile, int] = {
38:     DepthProfile.QUICK: 5,
39:     DepthProfile.STANDARD: 15,
40:     DepthProfile.THOROUGH: 100,
41: }
42: 
43: DEPTH_PROVER_CAPS: dict[DepthProfile, int] = {
44:     DepthProfile.QUICK: 20,
45:     DepthProfile.STANDARD: 30,
46:     DepthProfile.THOROUGH: 10_000,
47: }
48: 
49: 
50: class ScanConfig(BaseModel):
51:     repo_path: str
52:     depth: DepthProfile = DepthProfile.STANDARD
53:     tier: int = 1
54:     severity_threshold: str = "low"
55:     output_formats: list[str] = Field(default_factory=lambda: ["json"])
56:     compliance_frameworks: list[str] = Field(default_factory=list)
57:     include_paths: list[str] | None = None
58:     exclude_paths: list[str] = Field(
59:         default_factory=lambda: ["tests/", ".git/", "examples/", ".terraform/"],
60:     )
61:     budget: BudgetConfig = Field(default_factory=BudgetConfig)
62: 
63:     @classmethod
64:     def from_input(cls, scan_input: CloudSecurityInput, repo_path: str) -> ScanConfig:
65:         depth = DepthProfile(scan_input.depth)
66:         budget = BudgetConfig(
67:             max_cost_usd=scan_input.max_cost_usd,
68:             max_duration_seconds=scan_input.max_duration_seconds,
69:         )
70:         if scan_input.max_concurrent_hunters is not None:
71:             budget.max_concurrent_hunters = scan_input.max_concurrent_hunters
72:         if scan_input.max_concurrent_provers is not None:
73:             budget.max_concurrent_provers = scan_input.max_concurrent_provers
74:         return cls(
75:             repo_path=repo_path,
76:             depth=depth,
77:             tier=scan_input.tier,
78:             severity_threshold=scan_input.severity_threshold,
79:             output_formats=scan_input.output_formats,
80:             compliance_frameworks=scan_input.compliance_frameworks,
81:             include_paths=scan_input.include_paths,
82:             exclude_paths=scan_input.exclude_paths,
83:             budget=budget,
84:         )
85: 
86: 
87: class AIIntegrationConfig(BaseModel):
88:     provider: str = Field(
89:         default_factory=lambda: os.getenv("CLOUDSECURITY_PROVIDER", os.getenv("HARNESS_PROVIDER", "aforge"))
90:     )
91:     harness_model: str = Field(
92:         default_factory=lambda: os.getenv(
93:             "CLOUDSECURITY_MODEL",
94:             os.getenv("HARNESS_MODEL", "openrouter/minimax/minimax-m2.5"),
95:         )
96:     )
97:     ai_model: str = Field(
98:         default_factory=lambda: os.getenv(
99:             "CLOUDSECURITY_AI_MODEL",
100:             os.getenv("AI_MODEL", os.getenv("CLOUDSECURITY_MODEL", "openrouter/minimax/minimax-m2.5")),
101:         )
102:     )
103:     max_turns: int = Field(default_factory=lambda: int(os.getenv("CLOUDSECURITY_MAX_TURNS", "50")))
104:     opencode_bin: str = Field(default_factory=lambda: os.getenv("CLOUDSECURITY_OPENCODE_BIN", "opencode"))
105:     aforge_bin: str = Field(
106:         default_factory=lambda: os.getenv(
107:             "CLOUDSECURITY_AFORGE_BIN",
108:             os.getenv("AFORGE_BIN", "aforge"),
109:         )
110:     )
111: 
112:     @classmethod
113:     def from_env(cls) -> AIIntegrationConfig:
114:         return cls()
115: 
116:     def provider_env(self) -> dict[str, str]:
117:         env_keys = (
118:             "OPENROUTER_API_KEY",
119:             "ANTHROPIC_API_KEY",
120:             "OPENAI_API_KEY",
121:             "GOOGLE_API_KEY",
122:             "AWS_ACCESS_KEY_ID",
123:             "AWS_SECRET_ACCESS_KEY",
124:             "AWS_SESSION_TOKEN",
125:             "AWS_REGION",
126:             "AWS_DEFAULT_REGION",
127:             "GOOGLE_APPLICATION_CREDENTIALS",
128:             "AZURE_CLIENT_ID",
129:             "AZURE_CLIENT_SECRET",
130:             "AZURE_TENANT_ID",
131:             "AZURE_SUBSCRIPTION_ID",
132:         )
133:         env: dict[str, str] = {key: value for key in env_keys if (value := os.getenv(key))}
134:         env["AGENTFIELD_AFORGE_COMMAND"] = os.getenv("AGENTFIELD_AFORGE_COMMAND", "exec")
135:         xdg = os.getenv("XDG_DATA_HOME") or os.path.join(tempfile.gettempdir(), "opencode-shared-data")
136:         os.makedirs(xdg, exist_ok=True)
137:         env["XDG_DATA_HOME"] = xdg
138:         return env
```
_import/usage context:_ IMPORTS: from __future__ import annotations, import os, import tempfile, from enum import Enum, from pydantic import BaseModel, Field, from .schemas.input import CloudSecurityInput
IMPORTED BY: none