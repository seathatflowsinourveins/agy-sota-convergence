---
id: ADR-0002
layer: L0
status: accepted
date: 2026-11-26
decision-makers: SOTA Convergence Swarm (Verified 2026-11-26)
consulted: [sota-ecosystem, cross-session, changelogs, best-practices]
informed: [verifier, coordinator]
---

# ADR-0002: L0 — Execution Isolation and Sandboxes (OS-Native Local + MicroVM/gVisor Cloud)

## Context and Problem Statement

Autonomous coding and research agents execute untrusted shell commands, generated code, build scripts, and third-party dependencies. Local interactive developer loops require sub-millisecond startup and direct access to local toolchains without Docker daemon friction, whereas multi-tenant cloud agent fleets, adversarial evaluations, and untrusted repository audits require hardware-level or user-space kernel isolation that shared-kernel containers cannot safely provide. How should Layer `L0` isolate agent execution cleanly without overlapping `L8` (policy evaluation) or inviting custom sandbox self-invention?

## Decision Drivers

- **Zero-Startup Local Ergonomics:** Local developer terminals must isolate filesystem mounts, sensitive credentials (`~/.ssh`, `.env`, `~/.aws`, `~/.docker`, `~/.kube`), and outbound domains with zero VM boot latency.
- **Hard Multi-Tenant Kernel Boundaries in Cloud:** Cloud execution of untrusted code must defeat container-escape and kernel-exploit vectors via hardware virtualization (Firecracker microVMs) or user-space syscall interception (gVisor) plus host-side egress firewalls.
- **Strict Layer Disjointness (`L0` vs. `L8`):** `L0` enforces kernel/OS/VM boundaries; `L8` authors and evaluates the declarative `Deny > Ask > Allow` policy rules compiled down into `L0`.
- **Fail-Safe Degradation:** When an OS sandbox primitive is unavailable (e.g., locked-down containers without unprivileged user namespaces or unsupported Windows builds), execution must degrade to interactive review rather than running silently unrestricted.
- **Zero Self-Invention:** Never wrap local interactive shells in custom Docker glue, hand-rolled `chroot` scripts, or custom seccomp profiles.

## Considered Options

1. **Option 1 (Chosen): Split Upstream Isolation — AGY OS-Native Sandbox Locally + Dedicated MicroVM/gVisor Sandboxes in Cloud** (`AGY` Linux kernel namespaces / macOS `sandbox-exec` Seatbelt / Windows AppContainer locally; `E2B` Firecracker, `Modal` gVisor, `Daytona` workspaces/VMs, and `Cloudflare` Containers/Sandbox SDK 1.0 in cloud).
2. **Option 2 (Rejected): Plain Docker Containers Everywhere (Local & Cloud).**
3. **Option 3 (Rejected): Custom In-House Shell Jail / Wrapper Script or Unrestricted Host Execution (`Turbo` / `--dangerously-skip-permissions`).**

## Decision Outcome

Chosen option: **Option 1 — Split Upstream Isolation (AGY OS-Native Sandbox Locally + Dedicated MicroVM/gVisor Sandboxes in Cloud)**, because it is the only option that delivers zero-latency workstation defense on macOS, Linux, and Windows while meeting multi-tenant cloud isolation requirements using pinned upstream engines.

### Consequences

- **Good:** Zero startup latency locally across Linux (native kernel namespaces), macOS (`sandbox-exec` Seatbelt SBPL), and Windows 11 24H2+ (AppContainer process security environments, AGY App `v2.15.1` / CLI `v1.2.17`); automatic credential blocking (`.env`, `~/.ssh`, `~/.docker`, `~/.kube`, `~/_netrc`, `~/.git-credentials`) and zero outbound network except `read_url`-derived `AllowedDomains`.
- **Good:** Cloud workloads gain sub-second Firecracker microVMs (`E2B`), high-density gVisor bursting (`Modal`), sub-90ms workspace forking (`Daytona`), or edge-proximate Containers with host-side egress credential isolation (`Cloudflare Sandbox SDK 1.0`).
- **Good:** Built-in fail-safe degradation (CLI `v1.4.4+`): unavailable local sandboxes automatically hide `auto` mode and fall back from `proceed-in-sandbox` to `request-review`.
- **Bad:** Local loopback RPCs (such as `ConversationService` on `http://$ANTIGRAVITY_LS_ADDRESS`) are blocked inside the local sandbox (`"Port ... not allowed for HTTP"` / HTTP `403`) and require scoped unsandboxed approval; Windows AppContainer leaves folders outside the user profile readable (though non-writable).
- **Neutral:** Multi-harness workstations running Codex CLI alongside AGY retain Codex CLI's own OS-native sandbox (Linux `bubblewrap`/seccomp + macOS Seatbelt) strictly within Codex sessions—never conflated with AGY's native Linux kernel namespaces.

### Confirmation

Execute the following automated fitness checks from the repository root:

```bash
# 1. Verify AGY CLI supports OS-native sandbox execution mode
agy --help | grep -q -- "--sandbox"

# 2. Verify repository baseline permissions enable terminal sandbox with zero tilde deny rules
python3 -m unittest tests/test_hooks_and_handoff.py -v

# 3. Verify zero custom Dockerfile/chroot/privileged wrappers exist in .agents/
! grep -rnE "(chroot|docker run.*--privileged|--dangerously-skip-permissions)" .agents/

# 4. Verify manifest seal & L0 disjointness gate pass cleanly
python3 scripts/verify_manifest.py --verify
```

## Pros and Cons of the Options

### Option 1: Split Upstream Isolation (AGY OS-Native Local + MicroVM/gVisor Cloud)
- **Pros:** Zero local daemon overhead; native integration with AGY `permissions.md` (`read_file`/`write_file` mounts + `read_url` -> `AllowedDomains`); hardware KVM (`Firecracker`) or user-space kernel (`gVisor`) containment for untrusted cloud execution; passes the 5-Question Zero-Self-Invention test (100% upstream runtimes, zero custom kernel/container glue, clean install without forks).
- **Cons:** Requires choosing the right cloud provider per workload shape (E2B for multi-tenant code interpreters, Modal for bursty evals/GPUs, Daytona for stateful forked workspaces, Cloudflare for edge/Code Mode).

### Option 2: Plain Docker Containers Everywhere
- **Pros:** Familiar developer tooling and portable OCI images.
- **Cons:** **Rejected** — shares the host Linux kernel (insufficient against adversarial or hallucinated kernel-escape exploits in multi-tenant cloud/eval runs); adds daemon startup latency, volume-mount permission friction on macOS, and breaks access to local host toolchains during interactive editing.

### Option 3: Custom Shell Jail / Unrestricted Host Execution
- **Pros:** Zero external dependencies.
- **Cons:** **Rejected (Fails Zero-Self-Invention Gate)** — custom shell parsers/regex jails are trivially bypassed by command smuggling (`$(...)`, symlinks, `fd -X`), while unrestricted `Turbo` / `--dangerously-skip-permissions` exposes host credentials and breaks defense-in-depth on untrusted repositories.

## Clean Upstream Installation & Adapter Boundary

| Scope | Canonical Upstream | Registry / Channel | Exact Verified Version (`2026-11-26`) | Clean Pinned Install Command | Post-Install Smoke / Verify Command |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Local OS-Native** | Antigravity Terminal Sandbox | Bundled in AGY App / `agy` CLI | App `2.35.2` / CLI `1.5.18` | Bundled (zero extra install; enable via `agy --sandbox` or `agentMode: "auto"`) | `agy --version && agy --help \| grep -- --sandbox` |
| **Cloud Firecracker microVM** | E2B Python SDK (`e2b`) | PyPI | `2.66.0` (`2026-11-26`) | `uv add "e2b==2.66.0"` *(or `e2b-code-interpreter==2.11.12`)* | `uv run python -c "import e2b; print(e2b.__version__)"` |
| **Cloud Stateful Workspaces** | Daytona Python SDK (`daytona`) | PyPI *(replaces deprecated `daytona-sdk`)* | `2.3.0` (`2026-11-26`) | `uv add "daytona==2.3.0"` | `uv run python -c "import daytona; print(daytona.__file__)"` |
| **Cloud gVisor Burst / GPU** | Modal Python SDK (`modal`) | PyPI | `1.6.4` (`2026-11-12`) | `uv add "modal==1.6.4"` | `uv run modal --version` |
| **Cloud Edge Containers** | Cloudflare Sandbox SDK (`@cloudflare/sandbox`) + Wrangler | npm | `@cloudflare/sandbox@1.0.3` / `wrangler@4.168.0` | `npm install --save-exact @cloudflare/sandbox@1.0.3 wrangler@4.168.0` | `npx wrangler --version` |

**Thin-Adapter Boundary:** Repository code supplies only declarative sandbox configuration (`.agents/templates/permissions.baseline.json` compiled by `L8` into AGY's OS sandbox, or `<= 50`-LOC cloud sandbox session wrappers invoking `e2b.Sandbox`, `daytona.Daytona`, `modal.Sandbox.create`, or `@cloudflare/sandbox`). Never vendor container runtimes, mutate host Docker daemons, or re-implement syscall filtering.

## More Information

- Antigravity Terminal Sandbox: `https://antigravity.google/docs/sandbox.md`
- Antigravity Permissions (Sandbox integration & `AllowedDomains`): `https://antigravity.google/docs/permissions.md`
- E2B Sandboxes: `https://e2b.dev/resources/best-code-execution-sandboxes-for-ai-agents`
- Daytona Cloud Computers: `https://www.daytona.io/`
- Modal Sandboxes: `https://modal.com/blog/top-code-agent-sandbox-products`
- Cloudflare Containers & Sandbox SDK 1.0: `https://blog.cloudflare.com/faster-agent-sandboxes`
- Repository Architecture & Registry: [Convergence Stack](../convergence-stack.md), [Clean Upstream Installation Registry](../clean-install-registry.md), [Manifest Guide](../manifest-guide.md)
