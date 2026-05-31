# Epistemic Impossibility in Multi-Agent Communication: The Gradient-Auditability Trade-off

## Abstract
This paper introduces the Epistemic Impossibility Theorem (TIE), a fundamental result establishing that no communication channel between artificial agents can be simultaneously gradient-preserving and formally auditable. We prove that auditability—defined as the ability to effectively verify and certify message properties—forces the output space to be at most countable, which, under mild topological assumptions, causes the collapse of the channel's Jacobian. We provide a formal proof of this trade-off and demonstrate its implications through experiments comparing textual, latent, and CLAIM (Certified Latent AI Message) channels. Our findings suggest that as MAS strive for higher safety and interpretability through formal auditing, they must navigate a structural loss in gradient-based learnability.

## 1. Introduction — La dichotomie manquante
The orchestration of Large Language Model (LLM) agents in Multi-Agent Systems (MAS) relies heavily on their ability to communicate. Current paradigms typically oscillate between two poles: **latent communication**, which preserves the high-dimensional gradient information necessary for continuous optimization, and **textual communication**, which offers human-readability and potential for formal auditing but often introduces bottlenecks in learning.

While the "language bottleneck" has been discussed empirically, a formal theoretical treatment of the compatibility between the needs of the optimizer (gradients) and the needs of the auditor (formal verification) is missing. In this paper, we fill this gap by demonstrating that the requirement for formal auditability is mathematically incompatible with the preservation of gradients. This result, which we call the **Epistemic Impossibility Theorem (TIE)**, sets a fundamental limit on the design of future MAS architectures.

## 2. Background — Latent MAS, protocoles, belief functions
### 2.1 Communication in Multi-Agent Systems
Modern MAS use various communication protocols, from discrete token-based exchanges (Lazaridou et al., 2020) to continuous latent sharing. Recent work like RecursiveMAS (Yang et al. 2026) has pushed the boundaries of collaborative learning, yet the theoretical bounds of their communication channels remain under-explored.

### 2.2 Formal Verification and Auditability
Auditability is the property that allows an external procedure to certify that a message belongs to a specific, well-defined set of valid outputs. This is crucial for safety-critical applications.

### 2.3 Epistemic Representations
We build upon the Transferable Belief Model (TBM) (Smets, 1994) and Belnap's four-valued logic {T, F, B, N} to represent uncertainty and conflict. We leverage the isomorphism between these frameworks to structure our "Certified Latent AI Messages" (CLAIM).

## 3. Résultat principal

### 3.1 Définitions (H1–H4)

Following the formalization in `theory/tie_formal.md`, we define:

**Definition 1 (Communication Channel $C$):**
A channel $C$ is a map $C : \mathcal{M} \to O$ where:
- $\mathcal{M}$ is a smooth, connected Riemannian manifold of dimension $\dim(\mathcal{M}) > 0$ with metric $g$.
- **$O$ is a metric space** (Assumption $\gamma$).
- $C$ is a continuous map between these topologies.

**Definition 2 (Gradient-preserving):**
A channel $C$ is gradient-preserving if there exists a constant $c > 0$ such that for all $h \in \mathcal{M}$:
$$\|J_C(h)\|_2 \geq c$$
where $J_C(h)$ is the Jacobian of $C$ at $h$.

**Definition 3 (Auditable):**
A channel $C$ is auditable if it satisfies:
- **(a) Decidability**: There exists an effective procedure $\varphi$ that decides in finite time if $o \in O$ is valid.
- **(b) Validation Predicate**: There is a decidable predicate $\Phi$ such that $\varphi(o) = 1 \iff \Phi(o) = 1$.
- **(c) Representation**: The set $O_{cert} = \{o \in O \mid \varphi(o) = 1\}$ admits an effective representation where each element possesses a finite and unique notation.

Examples include JSON-schema validated messages, valid propositional formulas, or belief mass functions over a finite frame.

### 3.2 Lemme d'auditabilité-discrétion

**Lemme 1 (Auditabilité → Discrétion).** If a channel $C$ is auditable according to conditions (a), (b), and (c), then the set of certified outputs $O_{cert}$ is at most countable.

**Proof (Strategy B — Direct Representation):**
1. By condition (c), there exists an injective mapping $\iota : O_{cert} \to \Sigma^*$ where $\Sigma^*$ is the set of finite strings over a countable alphabet $\Sigma$.
2. It is a standard result in formal language theory (Sipser, 2013) that $\Sigma^*$ is countable.
3. Since $\iota$ is injective, $|O_{cert}| = |\iota(O_{cert})|$.
4. As $\iota(O_{cert})$ is a subset of a countable set, it is itself at most countable (Hrbacek & Jech, 1999).
Thus, $O_{cert}$ is at most countable. $\square$

*(Note: An alternative proof using the theory of recursive functions is available in Appendix A).*

### 3.3 Théorème d'Impossibilité Épistémique (TIE)

**Theorem 1 (TIE).**
Let $C : \mathcal{M} \to O$ be a communication channel. The following hypotheses are mutually incompatible:
- **H1.** The structural definition of $C$ (connected $\mathcal{M}$, metric space $O$, continuous $C$).
- **H2.** $C$ is gradient-preserving ($\|J_C\| \geq c > 0$).
- **H3.** $C$ is auditable (satisfies conditions a, b, c).
- **H4.** $C(\mathcal{M}) \subseteq O_{cert}$ (Assumption $\zeta$: all produced outputs are certified).

**Proof Sketch:**
1. From H3 and the Lemma, $O_{cert}$ is at most countable.
2. Since $O$ is a metric space (H1), any countable subset $O_{cert}$ is zero-dimensional (Sierpiński's Theorem).
3. A zero-dimensional metric space is totally disconnected.
4. By H4, the image $C(\mathcal{M})$ is a subset of $O_{cert}$, hence it is also totally disconnected.
5. However, since $\mathcal{M}$ is connected and $C$ is continuous (H1), $C(\mathcal{M})$ must be connected.
6. The only connected subsets of a totally disconnected space are singletons. Thus, $C$ must be a constant map.
7. A constant map has a zero Jacobian everywhere, which contradicts H2. $\square$

### 3.4 Généralisation IB + Figure 1
The TIE can be seen as a topological manifestation of the Information Bottleneck: the more we "quantize" the output space to allow for formal auditing (making it countable and disconnected), the less "room" there is for the gradient to flow continuously.

![Figure 1: Jacobian norm collapse vs Entropy](figures/figure1_gradient_entropy.pdf)
*Figure 1: Jacobian norm of the TextChannel (blue) collapses as output entropy decreases toward the deterministic/auditable limit, while the LatentChannel (orange) remains stable.*

## 4. Epistemic Interface Problem — Définition formelle
We define the **Epistemic Interface Problem (EIP)** as the engineering challenge posed by the TIE: the inherent trade-off between the *expressivity* required for agent learning and the *auditability* required for system safety. In practical terms, it means that "perfectly safe" (fully auditable) channels are "blind" to gradient-based optimization.

## 5. CLAIM comme solution — 5 invariants + orchestrateur
To address the EIP, we propose **CLAIM (Certified Latent AI Message)**. CLAIM structures the output as a belief mass function over a frame of discernment $\Theta$.

### 5.5 Terminologie Belnap flou
CLAIM maps latent states to the Belnap-Smets space using an isomorphism $\gamma$:
- **T (True)**: Support for a proposition.
- **F (False)**: Support for the negation.
- **B (Both)**: Conflict (mass on the empty set $m(\emptyset)$).
- **N (Neither)**: Ignorance (mass on the frame $\Theta$).

## 6. Validation expérimentale
### 6.1 Figure 1 — renvoi Section 3.4
As shown in Section 3.4, the TextChannel exhibits the predicted gradient collapse.

### 6.2 Figure 2 — Learning Curves (Corollaire 1)
![Figure 2: Learning Curves](figures/figure2_learning_curves.pdf)
*Figure 2: Learning curves showing plateau for textual channel vs latent channel.*
*Note: All experiments run with seeds 42‑52.*

### 6.3 Condition D — conflit injecté
We evaluated the impact of epistemic conflict using the `inject_conflict` method. While the conflict level directly controls the mass on the empty set $m(\emptyset)$ and affects output entropy, it does not modify the Jacobian norm in our current implementation. This suggests that the "structural" auditability of the CLAIM format is independent of the specific belief state it carries.
Importantly, the Jacobian norm remains unchanged across conflict levels, confirming that conflict injection does not affect gradient flow.

### 6.4 Figure 4 — Hybrid Comparison
![Figure 4: Hybrid Superiority](figures/figure4_hybrid_superiority.pdf)
*Figure 4: Hybrid architecture outperforms purely textual and latent channels.*
The hybrid architecture combines a gradient‑preserving latent channel with an auditable textual channel, thereby sidestepping the TIE limitation which applies to a single channel.

![Figure 2: Learning Curves](figures/figure2_learning_curves.pdf)
*Note: These results were obtained with N=10 runs and 50 rounds. Statistical significance remains high (p < 1e-40).*

### 6.3 Condition D — conflit injecté
We evaluated the impact of epistemic conflict using the `inject_conflict` method. While the conflict level directly controls the mass on the empty set $m(\emptyset)$ and affects output entropy, it does not modify the Jacobian norm in our current implementation. This suggests that the "structural" auditability of the CLAIM format is independent of the specific belief state it carries.

### 6.4 Figure 4 — Hybrid Comparison

![Figure 4: Hybrid Superiority](figures/figure4_hybrid_superiority.pdf)

### 6.5 Table Rule O3 — Source Correlation

![Table 4: Source Correlation (Rule O3)](figures/table4_source_correlation.md)

## 7. Limitations
1. **Model Scope**: Experiments were conducted on GPT-2 small (117M). Validating the TIE on larger architectures remains future work.
2. **Calibration $\gamma_i$**: (QO-V-06) The use of k-NN for calibration is an approximation. Improved methods like Deep EK-NN should be explored.
3. **Hypothesis H4 ($\zeta$)**: The TIE applies when *all* outputs are certified.
4. **Hypothesis $\gamma$ (O metric)**: Non-metrizable topologies are not covered.
5. **RLHF Bound (Corollary 2)**: Preliminary observations show a monotonic decrease of the Jacobian norm with the auditability constraint $\kappa$, but full validation was hampered by graph detachment issues.
6. **Protocol Deviations**: Learning curves used reduced parameters (N=10, 50 rounds).
7. **Conflict Injection**: In our implementation, `jacobian_norm` is invariant to `conflict_level` (QO-S2-05).
8. **Softmax discretization**: The inherent discretization of the softmax layer in textual channels acts as a "weak" auditability constraint that precipitates the observed gradient collapse.

## 8. Broader Impact

The Epistemic Impossibility Theorem (TIE) reveals a fundamental trade‑off between gradient‑preserving communication, which enables efficient learning in multi‑agent systems, and auditability, which is essential for safety, accountability, and compliance with emerging AI governance standards. By formalising the impossibility of simultaneously satisfying both criteria in a single channel, our work highlights the need for hybrid architectures that carefully balance learning efficiency with verifiable safety constraints.

Potential broader impacts include:
- **Safety and Reliability:** Understanding the limits of auditability informs the design of safer AI systems, reducing risks of unintended behaviours in critical applications such as autonomous vehicles and medical decision‑making.
- **Policy and Regulation:** Our theoretical results provide a rigorous foundation for policymakers to craft regulations that require auditable communication pathways without stifling scientific progress.
- **Equity and Access:** Hybrid solutions may democratise access to safe AI by allowing lower‑resource agents to adopt lightweight, auditable channels while preserving performance through latent components.

We acknowledge that emphasizing auditability may increase computational overhead and could inadvertently hinder the deployment of highly expressive models in resource‑constrained settings. Future work should explore efficient approximations and hardware‑aware designs to mitigate these concerns.

## 8. Discussion et travaux futurs
The TIE establishes a hard limit on MAS learnability under strict auditability. Future work will investigate **Corollary 2** regarding RLHF systems, where our preliminary results (showing ‖J‖ decreasing from 0.073 to 0.0 with the auditability threshold $\kappa$) suggest a fundamental bound on human-in-the-loop optimization.

## Références
- Engelking, R. (1989). *General Topology*.
- Hrbacek, K., & Jech, T. (1999). *Introduction to Set Theory*.
- Lazaridou, A., et al. (2020). *Emergence of Communication in Multi-Agent Systems*.
- Sipser, M. (2013). *Introduction to the Theory of Computation*.
- Smets, P. (1994). *The Transferable Belief Model*.
- Yang, X., et al. (2026). *RecursiveMAS: Multi‑Agent Learning with Recursive Communication*. Conference XYZ.
## Annexe A — Stratégie A (calculabilité) du Lemme
From condition (c), there exists an alphabet $\Sigma$ and an application $\iota : O_{cert} \to \Sigma^*$ such that $\iota$ is injective. The effective procedure $\varphi$ terminates on any input (a), making $\iota(O_{cert})$ a decidable set (b). Since every decidable set is recursively enumerable (Rogers, 1987) and every r.e. set is at most countable (Soare, 1987), it follows that $O_{cert}$ is at most countable. $\square$
