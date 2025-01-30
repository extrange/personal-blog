---
date: 2025-01-30
categories:
  - Philosophy
---

# Large Reasoning Models and Intelligence

Toward the end of 2024, a new type of language model was released: the Large Reasoning Model, or LRM. Examples include OpenAI's [o1], Qwen's [QwQ] and Deepseek's [R1]. Unlike traditional Large Language Models (LLMs), these models improve their accuracy by performing test-time compute, generating long reasoning chains before outputting their answer.

In the prior discussion on the [measures of intelligence], the intelligence of a system is defined as its skill-acquisition efficiency, when given a set of priors and experience. A more intelligent system would end up with greater skill after undergoing a similar amount of experience as a less intelligent system. In essence, this is the measure of the generalization ability of the system in a particular domain.

This article is an exploration into whether LRMs and the method of generating reasoning chains represent a path toward higher intelligence as defined above.

<!-- more -->

## Introduction

The current technique of training models to reason, as revealed by Deepseek's [R1], consists in training the model via reinforcement learning. In particular, this can be done without any supervised data. Verification is performed by requiring the model to output the answer in a specified format, which can be automatically verified by rules (e.g. code can be tested to be compilable, while solutions to math problems can be compared directly).

This process of training produces several emergent abilities, which were not present in the precedent LLMs:

- Difficulty Estimation: The ability to identify hard problems (or problems requiring more reasoning), and spend more time reasoning on them.
- Self Correction: The ability to correct itself, right after it outputs an erroneous statement, instead of continuing to (wrongly) justify itself.
- Reflection: The ability to autonomously reflect on whether its proposed answer is correct (without prompting), and if not, try another, often repeatedly.

## Are LRMs reasoning like us?

It is easy to anthropormorphize these models and say that they reason like us, that perhaps their internal monologue represents the way we approach problems given their readable chains of reasoning.

However, there are several behaviors which suggest this may not be the case.

R1-Zero is the version of R1 trained purely by RL, without any Supervised Fine Tuning (SFT) data, such as human annotated chains of reasoning. In essence it was provided with questions, and rewards were given based on correctness of the final response and adherence to putting its thinking process between specified tags.

The Deepseek team found that R1-Zero had issues with poor readability and language mixing in its output. As a result, they gathered a dataset of labelled Chain of Thought (CoT) data and pretrained the base model on it, before applying the same RL process as R1-Zero. The resulting model produced outputs which were more human readable and performance was slightly better in some domains.

The team behind the ARC AGI benchmark (a test for general intelligence, of which the creator of also defined intelligence as mentioned above), noted the [following][arc-agi-r1] about Deepseek's reasoning models, in particular R1-Zero:

1. SFT data, for example via human annotated reasoning chains, is not necessary for accurate and legible Chain of Thought (CoT) reasoning in strongly verifiable domains.
2. The R1-Zero training process is capable of creating its own internal domain specific language (“DSL”) in token space via RL optimization.
3. SFT is necessary for increasing CoT reasoning domain generality.

These claims are examined:

**Claim (1)** suggests that the problem of illegible outputs that Deepseek encountered with R1-Zero did not appear during the ARC AGI benchmark.

It is interesting to speculate why this is the case - perhaps the ARC AGI dataset simply did not cause the model to enter that part of the token space where the illegibility that the creators found resides?

**Claim (2)** is more important and suggests that the model is using these reasoning tokens (possibly illegible to us) as its own language for solving a problem.

The implication is that the model is using our language to reason, but not in a way we normally understand (or else they would not be illegible to us). Taken further, it could mean that these models are reasoning in a completely inhuman way, one which we may never be able to understand, but which the outputs are verifiably correct.

**Claim (3)** tempers the implications of Claim (2) somewhat, and suggests that pretraining on SFT data helps the model to generalize.

Why this is the case isn't clear. Perhaps SFT data contains traces of reasoning relevant for other domains? Or more broadly, only models which reason in a human-like manner can achieve generalizability (as perceived by humans - see [this discussion][generality-of-human-intelligence] for why intelligence must have a defined scope). If this is true, it would mean that achieving generalizability is only possible by human chains of reasoning.

## Challenges

Here we examine both practical and philosophical challenges with this approach.

### Domains with non-verifiable rewards

While it is likely to [see LRMs improving][reasoning-models-generalize] on domains with verifiable solutions, such as math and coding, the same cannot be easily said on domains [without easily verifiable solutions][non-verifiable-rewards], such as literature, poetry, or even the question of which theorem is more useful.

In such domains, there is often no objective truth to base rewards on. For example, deciding which piece of poetry is better, or which story is more engaging.

How are we going to train the models if there is no objective truth to ground on?

### The process of discovery

Suppose we wanted to train the models to discover new theorems in say, physics or math.

One approach would be to collect a set of knowledge priors that we believe the discovers had at the time - e.g. the collection of all 18th century science, in the case of Einstein, and then perform RL on these models until they discovered the theory of relativity.

While we don't know if this approach will work, this raises the question of whether language alone is sufficient for reasoning.

In his discovery of relativity, did Einstein use aspects of the physical world, such as his perception of space and/or time, which we cannot put into language, and which were crucial to the discovery? If so, then it might be the case that these models will not be able to reproduce the theory given only language.

But how can we overcome this - how do we encode the information which we cannot put into words, into a model?

### Similarity to human reasoning

Assuming human reasoning is required for generalizability, how much do the CoT outputs of these models resemble human reasoning?

When we think of the solution to a problem, we do not necessarily generate a long CoT in our head - solutions sometimes appear to us suddenly. What is going on in our brains when this happens? Are we even conscious of the process?

That said, there are several reasons why these models may still be performing human-like reasoning:

- These models are internally performing human-like reasoning (via their weights), despite the CoT tokens they are outputting. Perhaps those tokens are used as a sort of scratchpad, and are not meant to convey any sort of intention about their internal state.
- Our human subconscious thought process is actually similar to the illegible tokens these models produce sometimes (bizarre if it were true)

Of course, it may not even be necessary to replicate human reasoning to achieve generalization.

## Is reasoning sufficient for generalization?

If reasoning were to truly allow for generalization, then we would see the following in upcoming LRMs:

- Reasoning trained models are well better in peak performance than existing autoregressive models in many domains we would not expect and are not necessarily verifiable, such as literature.
- Even if we train the model on simpler but verifiable tasks such as 'does this code compile', it eventually learns to write code that solves different tasks, e.g. LeetCode.

Till we see these aspects, the question remains unanswered.

[o1]: https://openai.com/o1/
[QwQ]: https://qwenlm.github.io/blog/qwq-32b-preview/
[R1]: https://arxiv.org/abs/2501.12948
[measures of intelligence]: 2022-12-27-on-the-measure-of-intelligence.md#defining-intelligence
[generality-of-human-intelligence]: 2022-12-27-on-the-measure-of-intelligence.md#the-generality-of-human-intelligence
[arc-agi-r1]: https://arcprize.org/blog/r1-zero-r1-results-analysis
[reasoning-models-generalize]: https://www.interconnects.ai/p/why-reasoning-models-will-generalize
[non-verifiable-rewards]: https://news.ycombinator.com/item?id=42868768
