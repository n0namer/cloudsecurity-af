# CloudSecurity-AF — LLM Provider & Security Profile

Status: canonical repo-local provider profile
Cross-component contract: `n0namer/universal-solver:main/docs/architecture/llm-provider-security-contract.md`

## Current source contract

`agentfield-package.yaml` currently declares:
- required `OPENROUTER_API_KEY`;
- optional `HARNESS_PROVIDER`;
- optional `HARNESS_MODEL`;
- optional `AI_MODEL` for direct AI calls;
- node-scoped cloud credentials (for example AWS access credentials) separately from LLM credentials;
- AgentField control-plane credentials separately.

The current LLM contract is therefore **OpenRouter-centric**. Cloud credentials are a separate capability and MUST NOT be conflated with model/provider credentials.

## Provider rule

CloudSecurity-AF may use both:
1. coding-agent harness calls;
2. direct AI calls.

These paths require independent provider/model/base verification when exercised.

## Gonka/OpenAI-compatible adoption rule

If CloudSecurity-AF is migrated to Gonka/OpenAI-compatible routing, prove before changing bootstrap/manifest requirements that:
- source/runtime supports `OPENAI_API_KEY` + `OPENAI_BASE_URL` end-to-end;
- selected model namespaces are explicit;
- harness/direct paths preserve custom base URL where applicable;
- no unintended OpenRouter fallback occurs.

Until that proof exists, current OpenRouter requirements remain source truth.

## Security requirements

- Never commit/log LLM credentials, AgentField credentials, or cloud access credentials.
- Cloud credentials are node-scoped secrets and require stricter separation from global LLM-provider secrets.
- Evidence/logs must redact account IDs, access keys, tokens, private resource names, and sensitive scan payloads where appropriate.
- Read-only cloud scanning permissions remain independent from LLM/provider correctness.
- Provider fallback MUST be explicit and observable.
- A successful cloud API scan does not prove LLM/provider correctness; a successful model call does not prove cloud access correctness.

## Acceptance ladder

1. Exact CloudSecurity-AF source/runtime identity known.
2. Package starts and node registers.
3. Cloud read-only credential scope/probe succeeds where required.
4. Intended harness/direct provider/model resolves.
5. Required provider key/base reaches the actual model client.
6. Minimal model call succeeds.
7. Execution evidence shows intended provider/model and no unintended fallback.
8. Cloud-security canary produces a semantically valid, evidence-grounded result without unintended writes.

Health/registration alone is not provider or semantic PASS.

## Failure classes

Use: `BOOTSTRAP_ADMISSION`, `MODEL_RESOLUTION`, `ENV_PROPAGATION`, `BASE_URL_LOSS`, `AUTH`, `FALLBACK`, `TRANSPORT`, `SEMANTIC`.

For cloud access failures, classify cloud-auth/scope separately from LLM-provider failures.

Patch the first failing layer only.
