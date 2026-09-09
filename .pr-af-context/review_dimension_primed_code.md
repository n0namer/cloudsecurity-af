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

### src/cloudsecurity_af/reasoners/phases.py
```
1: from __future__ import annotations
2: 
3: import asyncio
4: import os
5: from typing import Any, cast
6: 
7: from cloudsecurity_af.config import DEPTH_CHAIN_LIMITS, DEPTH_HUNTER_MAP, DEPTH_PROVER_CAPS, DepthProfile
8: from cloudsecurity_af.schemas.chain import ChainResult
9: from cloudsecurity_af.schemas.hunt import HuntResult, RawFinding
10: from cloudsecurity_af.schemas.prove import RemediationSuggestion, Verdict, VerifiedFinding
11: from cloudsecurity_af.schemas.recon import (
12:     DriftReport,
13:     ReconResult,
14:     ResourceGraph,
15:     ResourceInventory,
16: )
17: from cloudsecurity_af.scoring import Severity
18: 
19: from . import router
20: 
21: _runtime_router: Any = router
22: NODE_ID = os.getenv("NODE_ID", "cloudsecurity")
23: 
24: 
25: def _unwrap(result: object, name: str) -> object:
26:     if isinstance(result, dict):
27:         if "error" in result and isinstance(result["error"], dict):
28:             message = result["error"].get("message") or result["error"].get("detail") or str(result["error"])
29:             raise RuntimeError(f"{name} failed: {message}")
30:         if "error_message" in result and result["error_message"]:
31:             raise RuntimeError(f"{name} failed: {result['error_message']}")
32:         if result.get("status") in ("failed", "error"):
33:             raise RuntimeError(f"{name} failed: {result.get('error_message', 'Unknown error')}")
34:         if "output" in result:
35:             return result["output"]
36:         if "result" in result:
37:             return result["result"]
38:     return result
39: 
40: 
41: def _as_dict(payload: object, name: str) -> dict[str, Any]:
42:     if not isinstance(payload, dict):
43:         raise RuntimeError(f"{name} returned non-dict payload: {type(payload).__name__}")
44:     return payload
45: 
46: 
47: def _normalize_depth(depth: str) -> DepthProfile:
48:     try:
49:         return DepthProfile(depth.lower())
50:     except ValueError:
51:         return DepthProfile.STANDARD
52: 
53: 
54: # ---------------------------------------------------------------------------
55: # RECON PHASE
56: # ---------------------------------------------------------------------------
57: 
58: 
59: @router.reasoner()
60: async def recon_phase(
61:     repo_path: str,
62:     depth: str = "standard",
63:     tier: int = 1,
64:     cloud_config: dict[str, Any] | None = None,
65: ) -> dict[str, Any]:
66:     iac_raw = await _runtime_router.call(
67:         f"{NODE_ID}.run_iac_reader",
68:         repo_path=repo_path,
69:     )
70:     inventory = ResourceInventory.model_validate(_as_dict(_unwrap(iac_raw, "run_iac_reader"), "run_iac_reader"))
71: 
72:     graph_raw = await _runtime_router.call(
73:         f"{NODE_ID}.run_resource_graph_builder",
74:         repo_path=repo_path,
75:         inventory_path=inventory.inventory_saved_path,
76:     )
77:     resource_graph = ResourceGraph.model_validate(
78:         _as_dict(_unwrap(graph_raw, "run_resource_graph_builder"), "run_resource_graph_builder")
79:     )
80: 
81:     drift_report = None
82:     live_inventory = None
83: 
84:     if tier >= 2 and cloud_config is not None:
85:         live_raw, drift_raw = await asyncio.gather(
86:             _runtime_router.call(
87:                 f"{NODE_ID}.run_cloud_connector",
88:                 cloud_config=cloud_config,
89:             ),
90:             _runtime_router.call(
91:                 f"{NODE_ID}.run_drift_detector",
92:                 iac_graph_path=resource_graph.graph_saved_path,
93:                 cloud_config=cloud_config,
94:             ),
95:         )
96:         live_inventory = ResourceInventory.model_validate(
97:             _as_dict(_unwrap(live_raw, "run_cloud_connector"), "run_cloud_connector")
98:         )
99:         drift_report = DriftReport.model_validate(
100:             _as_dict(_unwrap(drift_raw, "run_drift_detector"), "run_drift_detector")
101:         )
102: 
103:     import json
104: 
105:     try:
106:         with open(inventory.inventory_saved_path, "r") as f:
107:             inv_data = json.load(f)
108:             if not isinstance(inv_data, dict):
109:                 inv_data = {"resources": []}
110:             raw_res = inv_data.get("resources", [])
111:             if not isinstance(raw_res, list):
112:                 raw_res = []
113:             providers = sorted({r.get("provider") for r in raw_res if isinstance(r, dict) and r.get("provider")})
114:     except Exception:
115:         providers = []
116: 
117:     recon = ReconResult(
118:         inventory=inventory,
119:         resource_graph=resource_graph,
120:         drift_report=drift_report,
121:         live_inventory=live_inventory,
122:         iac_type=inventory.iac_type,
123:         providers_detected=providers,
124:         total_resources=inventory.total_resources,
125:         total_edges=resource_graph.total_edges,
126:     )
127:     return recon.model_dump()
128: 
129: 
130: def _cross_hunter_dedup(findings: list[RawFinding]) -> list[RawFinding]:
131:     sev_rank = {Severity.CRITICAL: 5, Severity.HIGH: 4, Severity.MEDIUM: 3, Severity.LOW: 2, Severity.INFO: 1}
132:     seen: dict[str, RawFinding] = {}
133:     for f in findings:
134:         primary_resource = f.resources[0].resource_id if f.resources else f.iac_file
135:         dedup_key = f"{primary_resource}::{f.category}"
136:         if dedup_key in seen:
137:             existing = seen[dedup_key]
138:             if sev_rank.get(f.estimated_severity, 0) > sev_rank.get(existing.estimated_severity, 0):
139:                 seen[dedup_key] = f
140:         else:
141:             seen[dedup_key] = f
142:     return list(seen.values())
143: 
144: 
145: # ---------------------------------------------------------------------------
146: # HUNT PHASE
147: # ---------------------------------------------------------------------------
148: 
149: 
150: @router.reasoner()
151: async def hunt_phase(
152:     repo_path: str,
153:     resource_graph_path: str,
154:     inventory_path: str,
155:     depth: str = "standard",
156:     max_concurrent_hunters: int = 3,
157: ) -> dict[str, Any]:
158:     profile = _normalize_depth(depth)
159:     active_hunters = DEPTH_HUNTER_MAP.get(profile, DEPTH_HUNTER_MAP[DepthProfile.STANDARD])
160: 
161:     concurrency_limit = max(1, min(max_concurrent_hunters, len(active_hunters)))
162:     findings_queue: asyncio.Queue[list[RawFinding]] = asyncio.Queue()
163:     semaphore = asyncio.Semaphore(concurrency_limit)
164: 
165:     async def _run_and_enqueue(hunter_name: str) -> None:
166:         async with semaphore:
167:             operation_name = f"run_{hunter_name}_hunter"
168:             try:
169:                 raw = await _runtime_router.call(
170:                     f"{NODE_ID}.{operation_name}",
171:                     repo_path=repo_path,
172:                     resource_graph_path=resource_graph_path,
173:                     inventory_path=inventory_path,
174:                     depth=depth,
175:                 )
176:                 payload = HuntResult.model_validate(_as_dict(_unwrap(raw, operation_name), operation_name))
177:                 await findings_queue.put(payload.findings)
178:             except Exception as exc:
179:                 await findings_queue.put([])
180: 
181:     async def _incremental_dedup() -> tuple[list[RawFinding], int]:
182:         all_findings: list[RawFinding] = []
183:         seen_fingerprints: set[str] = set()
184:         completed = 0
185:         total_raw = 0
186: 
187:         while completed < len(active_hunters):
188:             batch = await findings_queue.get()
189:             completed += 1
190:             total_raw += len(batch)
191: 
192:             for finding in batch:
193:                 fp = finding.fingerprint
194:                 if not fp:
195:                     fp = f"{finding.iac_file}:{finding.iac_line}:{finding.category}"
196:                     finding.fingerprint = fp
197:                 if fp in seen_fingerprints:
198:                     continue
199:                 seen_fingerprints.add(fp)
200:                 all_findings.append(finding)
201: 
202:         return _cross_hunter_dedup(all_findings), total_raw
203: 
204:     producers = [asyncio.create_task(_run_and_enqueue(h)) for h in active_hunters]
205:     consumer = asyncio.create_task(_incremental_dedup())
206: 
207:     await asyncio.gather(*producers)
208:     deduped, total_raw = await consumer
209: 
210:     hunt = HuntResult(
211:         findings=deduped,
212:         total_raw=total_raw,
213:         deduplicated_count=len(deduped),
214:         strategies_run=active_hunters,
215:         hunt_duration_seconds=0.0,
216:     )
217:     return hunt.model_dump()
218: 
219: 
220: # ---------------------------------------------------------------------------
221: # CHAIN PHASE
222: # ---------------------------------------------------------------------------
223: 
224: 
225: @router.reasoner()
226: async def chain_phase(
227:     findings: list[dict[str, Any]],
228:     resource_graph_path: str,
229:     drift_report: dict[str, Any] | None = None,
230:     depth: str = "standard",
231:     max_children: int = 3,
232: ) -> dict[str, Any]:
233:     profile = _normalize_depth(depth)
234:     max_paths = DEPTH_CHAIN_LIMITS.get(profile, 15)
235: 
236:     raw = await _runtime_router.call(
237:         f"{NODE_ID}.run_path_constructor",
238:         findings=findings,
239:         resource_graph_path=resource_graph_path,
240:         max_paths=max_paths,
241:         max_children=max_children,
242:         drift_report=drift_report,
243:     )
244:     chain = ChainResult.model_validate(_as_dict(_unwrap(raw, "run_path_constructor"), "run_path_constructor"))
245:     return chain.model_dump()
246: 
247: 
248: # ---------------------------------------------------------------------------
249: # PROVE PHASE
250: # ---------------------------------------------------------------------------
251: 
252: 
253: def _prioritize_findings(findings: list[RawFinding]) -> list[RawFinding]:
254:     sev = {Severity.CRITICAL: 5, Severity.HIGH: 4, Severity.MEDIUM: 3, Severity.LOW: 2, Severity.INFO: 1}
255:     return sorted(findings, key=lambda f: sev