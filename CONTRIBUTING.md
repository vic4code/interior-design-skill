# Contributing

Help people turn room ideas into editable models and dimensioned coordination drawings. Preserve one dimensional source, explicit assumptions and reproducible outputs.

Keep runtime resources inside `skills/interior-design/` so an installed skill works independently of the repository checkout. Follow the [Anthropic skill-creator structure](https://github.com/anthropics/skills/tree/main/skills/skill-creator): concise instructions, progressively loaded references, reusable scripts and bundled assets. Keep both READMEs aligned.

Before a pull request, run the unit tests from the repository root:

```bash
skills/interior-design/.venv/bin/python -m unittest discover -s tests -v
```

Then, from `skills/interior-design/`, generate and verify the sample and build the viewer:

```bash
.venv/bin/python scripts/project.py build assets/example-project.json --out assets/viewer/public/generated --blender
.venv/bin/python scripts/verify_outputs.py assets/viewer/public/generated
npm --prefix assets/viewer run build
```

Report platform limitations and distinguish passed checks from unverified paths. Keep the core free of required paid API calls. Publish synthetic fixtures and assets cleared for redistribution; document third-party source, author, licence and permitted use. Keep private project content and generated user projects out of Git. Describe unreviewed drawings as coordination drafts.

Report mm/metre conversions and mark breaking schema changes. Improve validation errors rather than relaxing checks merely to make a failing input pass. Use `docs/reviews/` for scoped work records containing acceptance criteria and dated verification results without personal runtime data.
