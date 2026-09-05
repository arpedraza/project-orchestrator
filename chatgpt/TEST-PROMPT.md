# ChatGPT Project Pilot Prompt

Use this in a disposable ChatGPT Project after loading the Project Orchestrator project instructions and source references.

---

I want to validate Project Orchestrator on a small but complete project.

Project objective:

> Build a small PowerShell utility that reads a JSON configuration file, validates required fields, writes a concise status report, and includes automated tests or a deterministic validation harness.

Constraints:

- Windows-first.
- Keep dependencies minimal.
- Do not deploy to production or modify cloud resources.
- Treat me, ChatGPT, Codex, and scripts as possible executors under the same work/evidence/gate contract.
- Manage the project using the Project Orchestrator operating model rather than fixed phases.
- Route work by capability.
- Keep canonical project facts separate from chat memory.
- Continue routine work autonomously inside the stated constraints.
- Escalate only genuine decisions outside delegated authority.
- Before handing execution to another chat/Codex/human, produce an Executor Checkpoint that makes the project resumable.

Start by establishing project control and telling me:

1. what canonical records/work items you need;
2. what can proceed now and what depends on something else;
3. which capabilities/executors are required;
4. the exact first execution boundary;
5. what you can do autonomously versus what would actually require a decision from me.

Do not claim local execution or repository changes unless the current environment actually provides those capabilities.
