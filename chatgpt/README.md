# Using Project Orchestrator in a ChatGPT Project

This mode is for testing/using Project Orchestrator as a **project operating model** inside ChatGPT without first installing it as a Codex skill.

## What this proves

A ChatGPT Project test primarily validates:

- conductor behavior;
- project-control discipline;
- capability-first routing;
- continuity across chats/executors;
- quality of work decomposition, decisions, RAID, handoffs, and escalation;
- whether the model relies on canonical project state instead of hidden chat memory.

It does **not** automatically prove local filesystem or terminal integration. Those depend on which tools the current ChatGPT environment exposes.

## Setup

1. Create a new ChatGPT Project for a disposable pilot project.
2. Copy the contents of `chatgpt/PROJECT-INSTRUCTIONS.md` into the Project's project-specific instructions.
3. Add the following Project Orchestrator source material to the Project so the chat can read it:
   - `SKILL.md`
   - `references/execution-continuity.md`
   - `references/operating-model.md`
   - `references/policy-authority.md`
   - `references/project-control-traceability.md`
   - `references/validation-rules.md`
4. Add the pilot project's canonical Markdown records/checkpoint as project sources when they exist and are not directly accessible through a connected executor.
5. Start a new chat with the prompt in `chatgpt/TEST-PROMPT.md` or a similarly small real project request.

## Expected behavior

The chat should:

- establish project identity/objective;
- create or propose canonical project-control records rather than using chat memory as truth;
- identify required capabilities and candidate executors;
- model work/dependencies/gates instead of running fixed numbered phases;
- continue routine work inside authority without repeatedly requesting approval;
- surface real capability gaps and authority decisions;
- produce a checkpoint before handing to another chat/Codex/human executor.

## Tool boundaries

If the ChatGPT Project cannot directly access the pilot repository or a local terminal, the orchestrator should not pretend that it performed those actions. It should instead produce an exact handoff/command for the human or Codex executor and then consume the returned result as execution evidence.

When GitHub, local folders, Codex, or another execution tool is available, treat it as an executor/integration under the same project policy. Tool availability never changes the canonical project-control model.

## Cross-chat test

After the first chat reaches a meaningful stopping point:

1. capture the generated Executor Checkpoint;
2. start a second chat in the same ChatGPT Project;
3. provide the checkpoint if it is not already available as a project source;
4. say: `Resume Project Orchestrator from the latest checkpoint.`

The second chat should validate project identity/current state and continue from the next eligible work without reconstructing the project from scratch.

## Codex handoff test

If you later hand execution to Codex:

1. provide the latest checkpoint and exact work handoff;
2. have Codex read the selected project/repository state directly;
3. record the run/result/evidence;
4. refresh the checkpoint before returning to ChatGPT.

The executor changes; the project workflow does not.
