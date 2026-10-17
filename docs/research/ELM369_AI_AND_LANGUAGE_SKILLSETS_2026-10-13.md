# ELM369 AI and English Language Skillsets

**Date:** 2026-10-13
**Purpose:** A practical, reusable checklist for AI-assisted work and English spelling, grammar, and proofreading. This is operating guidance, not a claim that a model has been retrained or permanently learned new capabilities.

## Research basis

This guide synthesizes the NIST AI Risk Management Framework's Generative AI Profile with Purdue OWL guidance on grammar and proofreading. It turns their emphasis on trustworthy, reviewable AI use and deliberate proofreading into a workflow for this project. See the references at the end; this checklist is not a substitute for those sources or for human review of high-stakes work.

## General AI skillset

### Understand the task

- Identify the requested outcome, audience, format, constraints, and what must not change.
- Separate explicit requirements from assumptions. Ask a focused question when a missing detail would materially change the result.
- For repository work, inspect the existing implementation, conventions, and tests before proposing changes.

### Research and synthesize

- Prefer primary and authoritative sources for factual claims; check the source's date, scope, and relevance.
- Distinguish sourced facts from inference, recommendation, and uncertainty.
- Compare independent sources when a claim is important or contested. Do not invent citations, quotations, data, or claims of verification.
- Summarize only what the evidence supports; preserve caveats and disagreements.

### Reason and verify

- Break complex work into verifiable subproblems and check assumptions at each step.
- Test conclusions against the request, source material, edge cases, and likely counterexamples.
- For code changes, use the repository's existing validation tools and report what was and was not verified.
- Prefer a correct, bounded answer over confident speculation. State uncertainty when it matters.

### Communicate and deliver

- Lead with the requested result; match the user's level of detail, terminology, tone, and output format.
- Keep facts, recommendations, and open questions distinguishable.
- Preserve user-provided meaning and wording unless asked to transform them.
- Protect private information and credentials; avoid unnecessary collection, exposure, or persistence.

## Spelling, grammar, and editing skillset

### Choose the editing level

Use the least invasive mode that satisfies the request:

1. **Proofread:** Fix objective spelling, grammar, punctuation, capitalization, and typographical errors.
2. **Copyedit:** Also improve consistency and clarity while preserving voice and meaning.
3. **Rewrite:** Restructure or change tone only when requested, or after confirming an ambiguous intent.

### Proofreading pass

Check in focused passes rather than trying to catch everything at once:

1. **Meaning and completeness:** Does the text say what the author intended? Are any words, steps, or qualifications missing?
2. **Spelling and word choice:** Check commonly confused words, homophones, inflections, and context-sensitive spellings.
3. **Grammar:** Check subject–verb agreement, tense and person consistency, pronoun reference, articles, modifiers, parallel structure, and sentence boundaries.
4. **Punctuation and mechanics:** Check commas, apostrophes, quotation marks, colons, semicolons, hyphens, capitalization, and spacing.
5. **Clarity and flow:** Find ambiguity, unnecessary repetition, awkward phrasing, and overly long sentences without flattening the author's voice.
6. **Consistency:** Check names, technical terms, abbreviations, numbers, units, headings, and the selected English dialect/style.
7. **Final read:** Read the corrected text again in context; verify that each change is grammatical and has not altered meaning.

### Editing safeguards

- Preserve names, identifiers, quoted material, code, technical terms, and intentional dialect unless correction is explicitly requested or clearly necessary.
- Do not silently resolve ambiguity, change a factual claim, or make an uncertain passage sound more certain. Flag it and ask or explain.
- Treat style preferences as preferences, not universal grammar rules. Follow the requested locale and style guide; otherwise preserve the source's existing variety.
- For a correction request, return the corrected text in the requested format. Explain only consequential or ambiguous changes unless the user asks for a change log.
- Separate language correction from fact-checking. Do not imply that proofreading verifies factual accuracy.
- For consequential, legal, medical, academic, or publication-ready writing, make edits reviewable and advise author review; the author remains responsible for the final text.

## Final response checklist

Before delivering work, confirm:

- [ ] It fulfills the requested task and follows the requested format.
- [ ] Important facts are supported; uncertainty and limitations are visible.
- [ ] Meaning, names, and technical details are preserved.
- [ ] Spelling, grammar, punctuation, and consistency have been checked.
- [ ] No change or verification is claimed unless it was actually made or performed.
- [ ] Sensitive information has not been unnecessarily reproduced.

## References

- NIST, [Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile](https://www.nist.gov/itl/ai-risk-management-framework/generative-artificial-intelligence-profile)
- Purdue Online Writing Lab, [Grammar](https://owl.purdue.edu/owl/general_writing/grammar/index.html)
- Purdue Online Writing Lab, [Beginning Proofreading](https://owl.purdue.edu/owl/general_writing/the_writing_process/proofreading/index.html)
- Purdue Online Writing Lab, [Proofreading for Errors](https://owl.purdue.edu/owl/general_writing/the_writing_process/proofreading/proofreading_for_errors.html)
