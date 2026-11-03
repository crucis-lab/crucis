# Working in Crucis

Crucis is the standalone causal-discovery auditing framework. Read README.md and
provenance/extraction.json for the extraction boundary. Historical instructions
copied under crucis_causal/docs/ describe earlier work; these current rules govern this
repository and supersede their old no-Git and cc-research path instructions.

- Make automatic local commits after each coherent, validated implementation,
  correction, documentation or design milestone. Read tools/skills/milestone-commit/SKILL.md.
  Stage explicit owned paths/hunks and inspect the index. Preserve other work.
- During initial extraction, make no commit until the independence, compatibility
  and research-preservation checks pass and the migration receipt records the split.
  After that recorded boundary, the earlier user-requested commit hold is lifted.
- Do not push, publish, merge, rewrite history, change visibility, or create public
  accounts/remotes without authorization for that action. Local commits are already
  authorized and do not require repeated permission.
- Run tools/commit_gate.py before committing; the hook validates the staged tree.
  Run the relevant package tests and record skipped/data-dependent checks honestly.
- Keep code under crucis_causal/, tests under tests/, and record ticket IDs in work products.
  Original research provenance is in provenance/. Never silently rebaseline evidence.
- CRUCIS_DATA_ROOT selects explicit historical evidence; never add that checkout
  or its analysis/harness directories to Python's import path. Shared helpers are
  owned under crucis_causal/_support/ with extraction provenance.
- Preserve native semantics, uncertainty, scoped gaps and identity/provenance.
  A metadata validation pass is not evidence of causal correctness or full native support.
- No paid API runs without explicit authorization. Never read/copy sibling .env
  files or credentials. Sealed seeds remain outside the shared project workspace.
- Protocol, threshold, scientific scoring and certificate/paper-port changes need
  explicit versioned review. Namespace/extraction changes do not adopt a new protocol.
- The research paper and frozen results stay in cc-research. Coordinate file
  ownership before moving active subsystem work; new changes must not overwrite it.
