# Conditional-plan diagnostic prompt diff

Version: conditional-plan-v1. The sole scientific edit appends the researcher-approved instruction to each original rendered prompt, separated by two LF bytes. All original bytes, including case content, remain an exact prefix. No wrapper/config/schema change. Original and diagnostic SHA-256 values are recorded per case in metadata/input_manifest.json. The instruction is in prompt/conditional_plan_instruction.txt.

## pilot-001

```diff
--- pilot-v0.1/pilot-001.md
+++ conditional-plan-v1/pilot-001.md
@@ -157,3 +157,26 @@
   11 |         if satisfies(mask, clauses):
   12 |             return True
   13 |     return False
+
+
+Whenever structural quantumizability = YES, always provide a
+conditional migration plan describing HOW the computation could be
+quantumized, even if practical suitability = NO or UNCERTAIN.
+
+The conditional migration plan describes a technically plausible
+quantum reformulation under stated assumptions. It does NOT imply a
+recommendation to deploy the quantum version.
+
+Therefore:
+
+    Structural = YES
+    Practical = NO / UNCERTAIN
+    Decision = REMAIN_CLASSICAL
+
+is still compatible with:
+
+    plan != null
+
+Any unresolved semantic, exactness, resource, encoding, oracle,
+certification, or feasibility requirement must remain explicitly
+identified inside the plan rather than being silently assumed away.
```

## pilot-002

```diff
--- pilot-v0.1/pilot-002.md
+++ conditional-plan-v1/pilot-002.md
@@ -154,3 +154,26 @@
    8 |         digest = hashlib.sha256(digest + event).digest()
    9 |         audit(index, digest.hex())
   10 |     return digest.hex()
+
+
+Whenever structural quantumizability = YES, always provide a
+conditional migration plan describing HOW the computation could be
+quantumized, even if practical suitability = NO or UNCERTAIN.
+
+The conditional migration plan describes a technically plausible
+quantum reformulation under stated assumptions. It does NOT imply a
+recommendation to deploy the quantum version.
+
+Therefore:
+
+    Structural = YES
+    Practical = NO / UNCERTAIN
+    Decision = REMAIN_CLASSICAL
+
+is still compatible with:
+
+    plan != null
+
+Any unresolved semantic, exactness, resource, encoding, oracle,
+certification, or feasibility requirement must remain explicitly
+identified inside the plan rather than being silently assumed away.
```

## pilot-003

```diff
--- pilot-v0.1/pilot-003.md
+++ conditional-plan-v1/pilot-003.md
@@ -151,3 +151,26 @@
    5 |                     if ((mask >> u) & 1) != ((mask >> v) & 1))
    6 |         best = max(best, score)
    7 |     return best
+
+
+Whenever structural quantumizability = YES, always provide a
+conditional migration plan describing HOW the computation could be
+quantumized, even if practical suitability = NO or UNCERTAIN.
+
+The conditional migration plan describes a technically plausible
+quantum reformulation under stated assumptions. It does NOT imply a
+recommendation to deploy the quantum version.
+
+Therefore:
+
+    Structural = YES
+    Practical = NO / UNCERTAIN
+    Decision = REMAIN_CLASSICAL
+
+is still compatible with:
+
+    plan != null
+
+Any unresolved semantic, exactness, resource, encoding, oracle,
+certification, or feasibility requirement must remain explicitly
+identified inside the plan rather than being silently assumed away.
```

## pilot-004

```diff
--- pilot-v0.1/pilot-004.md
+++ conditional-plan-v1/pilot-004.md
@@ -151,3 +151,26 @@
    5 |         if code == target:
    6 |             return True
    7 |     return False
+
+
+Whenever structural quantumizability = YES, always provide a
+conditional migration plan describing HOW the computation could be
+quantumized, even if practical suitability = NO or UNCERTAIN.
+
+The conditional migration plan describes a technically plausible
+quantum reformulation under stated assumptions. It does NOT imply a
+recommendation to deploy the quantum version.
+
+Therefore:
+
+    Structural = YES
+    Practical = NO / UNCERTAIN
+    Decision = REMAIN_CLASSICAL
+
+is still compatible with:
+
+    plan != null
+
+Any unresolved semantic, exactness, resource, encoding, oracle,
+certification, or feasibility requirement must remain explicitly
+identified inside the plan rather than being silently assumed away.
```

## pilot-005

```diff
--- pilot-v0.1/pilot-005.md
+++ conditional-plan-v1/pilot-005.md
@@ -167,3 +167,26 @@
    1 | def prepare_offers(offers: list[dict]) -> list[dict]:
    2 |     eligible = [dict(offer) for offer in offers if offer["available"]]
    3 |     return sorted(eligible, key=lambda offer: offer["sku"])
+
+
+Whenever structural quantumizability = YES, always provide a
+conditional migration plan describing HOW the computation could be
+quantumized, even if practical suitability = NO or UNCERTAIN.
+
+The conditional migration plan describes a technically plausible
+quantum reformulation under stated assumptions. It does NOT imply a
+recommendation to deploy the quantum version.
+
+Therefore:
+
+    Structural = YES
+    Practical = NO / UNCERTAIN
+    Decision = REMAIN_CLASSICAL
+
+is still compatible with:
+
+    plan != null
+
+Any unresolved semantic, exactness, resource, encoding, oracle,
+certification, or feasibility requirement must remain explicitly
+identified inside the plan rather than being silently assumed away.
```

## pilot-006

```diff
--- pilot-v0.1/pilot-006.md
+++ conditional-plan-v1/pilot-006.md
@@ -152,3 +152,26 @@
    6 |         value += sum(w * bits[i] * bits[j] for i, j, w in couplings)
    7 |         best = value if best is None else min(best, value)
    8 |     return best
+
+
+Whenever structural quantumizability = YES, always provide a
+conditional migration plan describing HOW the computation could be
+quantumized, even if practical suitability = NO or UNCERTAIN.
+
+The conditional migration plan describes a technically plausible
+quantum reformulation under stated assumptions. It does NOT imply a
+recommendation to deploy the quantum version.
+
+Therefore:
+
+    Structural = YES
+    Practical = NO / UNCERTAIN
+    Decision = REMAIN_CLASSICAL
+
+is still compatible with:
+
+    plan != null
+
+Any unresolved semantic, exactness, resource, encoding, oracle,
+certification, or feasibility requirement must remain explicitly
+identified inside the plan rather than being silently assumed away.
```

## pilot-007

```diff
--- pilot-v0.1/pilot-007.md
+++ conditional-plan-v1/pilot-007.md
@@ -151,3 +151,26 @@
    5 |         if total == target:
    6 |             return True
    7 |     return False
+
+
+Whenever structural quantumizability = YES, always provide a
+conditional migration plan describing HOW the computation could be
+quantumized, even if practical suitability = NO or UNCERTAIN.
+
+The conditional migration plan describes a technically plausible
+quantum reformulation under stated assumptions. It does NOT imply a
+recommendation to deploy the quantum version.
+
+Therefore:
+
+    Structural = YES
+    Practical = NO / UNCERTAIN
+    Decision = REMAIN_CLASSICAL
+
+is still compatible with:
+
+    plan != null
+
+Any unresolved semantic, exactness, resource, encoding, oracle,
+certification, or feasibility requirement must remain explicitly
+identified inside the plan rather than being silently assumed away.
```

## pilot-008

```diff
--- pilot-v0.1/pilot-008.md
+++ conditional-plan-v1/pilot-008.md
@@ -152,3 +152,26 @@
    6 |         for _ in range(copies):
    7 |             output.append(list(normalized))
    8 |     return output
+
+
+Whenever structural quantumizability = YES, always provide a
+conditional migration plan describing HOW the computation could be
+quantumized, even if practical suitability = NO or UNCERTAIN.
+
+The conditional migration plan describes a technically plausible
+quantum reformulation under stated assumptions. It does NOT imply a
+recommendation to deploy the quantum version.
+
+Therefore:
+
+    Structural = YES
+    Practical = NO / UNCERTAIN
+    Decision = REMAIN_CLASSICAL
+
+is still compatible with:
+
+    plan != null
+
+Any unresolved semantic, exactness, resource, encoding, oracle,
+certification, or feasibility requirement must remain explicitly
+identified inside the plan rather than being silently assumed away.
```

## pilot-009

```diff
--- pilot-v0.1/pilot-009.md
+++ conditional-plan-v1/pilot-009.md
@@ -170,3 +170,26 @@
    4 |     if any(a < 0 or b < 0 or a >= len(jobs) or b >= len(jobs) or penalty < 0
    5 |            for a, b, penalty in links):
    6 |         raise ValueError("invalid placement link")
+
+
+Whenever structural quantumizability = YES, always provide a
+conditional migration plan describing HOW the computation could be
+quantumized, even if practical suitability = NO or UNCERTAIN.
+
+The conditional migration plan describes a technically plausible
+quantum reformulation under stated assumptions. It does NOT imply a
+recommendation to deploy the quantum version.
+
+Therefore:
+
+    Structural = YES
+    Practical = NO / UNCERTAIN
+    Decision = REMAIN_CLASSICAL
+
+is still compatible with:
+
+    plan != null
+
+Any unresolved semantic, exactness, resource, encoding, oracle,
+certification, or feasibility requirement must remain explicitly
+identified inside the plan rather than being silently assumed away.
```

## pilot-010

```diff
--- pilot-v0.1/pilot-010.md
+++ conditional-plan-v1/pilot-010.md
@@ -157,3 +157,26 @@
   11 | def check_records(payloads: list[str], target: str) -> bool:
   12 |     records = [json.loads(payload) for payload in payloads]
   13 |     return contains_record(records, target)
+
+
+Whenever structural quantumizability = YES, always provide a
+conditional migration plan describing HOW the computation could be
+quantumized, even if practical suitability = NO or UNCERTAIN.
+
+The conditional migration plan describes a technically plausible
+quantum reformulation under stated assumptions. It does NOT imply a
+recommendation to deploy the quantum version.
+
+Therefore:
+
+    Structural = YES
+    Practical = NO / UNCERTAIN
+    Decision = REMAIN_CLASSICAL
+
+is still compatible with:
+
+    plan != null
+
+Any unresolved semantic, exactness, resource, encoding, oracle,
+certification, or feasibility requirement must remain explicitly
+identified inside the plan rather than being silently assumed away.
```
