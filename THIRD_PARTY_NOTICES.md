# Third-party attribution

Tickets: DLV-09, DLV-10, INF-06

## NOTEARS reference implementation

`crucis_causal/_support/notears_linear.py` adapts the linear NOTEARS reference algorithm
by Xun Zheng and the NOTEARS authors. The scientific reference is Zheng, Aragam,
Ravikumar and Xing, *DAGs with NO TEARS: Continuous Optimization for Structure
Learning*, NeurIPS 2018.

- Upstream: https://github.com/xunzheng/notears
- Reference source reviewed during publication preparation:
  https://github.com/xunzheng/notears/blob/7786138ff43462b42b0632d0b4784f496b4b08e6/notears/linear.py
- Upstream license at that revision: Apache License 2.0. Its complete text is
  retained in `LICENSES/NOTEARS-Apache-2.0.txt`, including in built distributions.
- No upstream root NOTICE file was found at that reviewed revision.
- The reviewed revision is a reference for this review, not a claim that the
  original research extraction recorded that exact upstream commit.

The local adaptation implements the least-squares loss only, retains the
augmented-Lagrangian/L-BFGS-B optimization, uses NumPy/SciPy, and follows the
historical study's parameter/threshold defaults. It was extracted from the
research helper and its imports moved into the Crucis namespace. Attribution
and packaging notices were added on 3 Nov 2026; this review does not change the
numerical implementation or rebaseline historical results.

## Research provenance and external systems

Crucis was extracted from Uzair Gheewala's `cc-research` development tree.
`provenance/extraction.json` records original paths and source-byte hashes,
including the numerical/recording helpers under `crucis_causal/_support/`. It explicitly
distinguishes the older research HEAD from uncommitted work captured at extraction.

System adapters and file-format readers are distinct from redistribution of the
systems or datasets they inspect. Causal-Copilot, CausalIQ, MATMCD, PyWhy-LLM,
the imperfect-expert causal-order system, causal-learn, GES, and benchmark data
retain their own authorship and terms. An adapter name is neither a license for
external code/data nor evidence of completed native support. In particular, a
research registry entry saying that an external repository shows no license must
not be interpreted as permission to redistribute or a general evaluation license.

NumPy/jsonschema and optional installed dependencies are obtained separately;
their source trees are not bundled here. Installing a dependency or reading
recorded evidence does not transfer its license to Crucis. The paper and research
results remain in https://github.com/uzairgheewala/cc-research.

Original framework code and accompanying technical documentation are licensed
under Apache-2.0; see LICENSE, NOTICE and CITATION.cff. Third-party notices and
the original source hashes above remain distinct from that original-work credit.
