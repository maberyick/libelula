# OpenMedPipe

**A skeleton for building production medical-imaging AI pipelines.**

Most medical-imaging AI dies between "it works in my notebook" and "the team uses it every day." OpenMedPipe is a small, opinionated **starting point** for the second part: a clean pattern for turning models into a pipeline that ingests a case, runs the right models, quality-checks the output, and serves a result — reliably and reproducibly.

It is **not** a framework you're locked into and **not** anyone's proprietary system. It's a scaffold you clone and make your own — like starting from a well-organized template instead of a blank folder.

> Built and maintained by [BARTEK LLC](https://bartekllc.org). Use it, fork it, ship it.

---

## What you get

- **One model contract** (`ModelPlugin`) — every model (yours, open-source, or a hosted API) implements the same tiny interface, so the rest of the system doesn't care what's inside. Add a model = implement one class.
- **A stage orchestrator** — `ingest → preprocess → run models → aggregate → QC → output`, each stage isolated, timed, and logged. Plain Python by default; swap in Airflow/Prefect/Dagster for production without touching your models.
- **Quality control** — a place to catch empty masks, out-of-range scores, and drift *before* a result is trusted.
- **An optional local-LLM assistant** — suggests which models to run for a case (via a local [Ollama](https://ollama.com) model, so data never leaves your hardware). It's a *suggestion* the operator accepts or edits — not autopilot. Falls back to a rule if Ollama isn't running.
- **Container + web stubs** — a Dockerfile template to wrap a model, and a minimal submission API.
- **Runs out of the box** with two placeholder models and a dummy image — zero external dependencies.

## Architecture

```
        ┌─────────────┐
        │  Submit API │  (web/ — Flask/FastAPI stub)
        └──────┬──────┘
               │
        ┌──────▼───────┐     ┌───────────────────────────────┐
        │ Orchestrator │◄────│ LLM assistant (optional, local)│  suggests the pipeline
        │ (pipeline/)  │     │  assistant/ — Ollama           │
        └──────┬───────┘     └───────────────────────────────┘
               │  runs, in order, each registered model:
        ┌──────▼───────────────────────────────┐
        │  Model A → Model B → …  (models/)     │  one common ModelPlugin contract
        │  (each wrappable in a container)      │
        └──────┬───────────────────────────────┘
               │
        ┌──────▼──────┐     ┌──────────────┐
        │     QC       │────▶│   Output      │  mask / score / report
        │  (qc/)       │     │  + run report │
        └──────────────┘     └──────────────┘
```

## Quickstart

```bash
git clone https://github.com/<you>/openmedpipe.git
cd openmedpipe
pip install -e .            # installs the package
python examples/run_local.py
```

Expected output:

```
Suggested pipeline: ['threshold-segmenter', 'region-scorer']
Status: ok
Score: {'score': 14.06}
QC: {'nonempty_mask': {'pass': True, 'coverage': 0.1406, ...}}
```

## Make it yours

1. **Add a model** — subclass `ModelPlugin` in `openmedpipe/models/`, implement `run()`, and `@register` it:
   ```python
   from openmedpipe.models.base import ModelPlugin, ModelResult
   from openmedpipe.models.registry import register

   @register
   class MySegmenter(ModelPlugin):
       name = "my-segmenter"
       modality = "oct-bscan"
       description = "Retinal layer segmentation."
       def run(self, case):
           mask = my_model(case["image"])
           return ModelResult(self.name, output=mask)
   ```
2. **Wire the stages** — edit the model list you pass to `run_case()`, or let the assistant suggest it.
3. **Add QC checks** in `openmedpipe/qc/checks.py`.
4. **Containerize** each model with `containers/Dockerfile.model`.
5. **Go to production** — replace `pipeline/orchestrator.py` with an Airflow DAG; the model contract, registry, QC, and assistant stay the same.

## What it is / isn't

| It IS | It ISN'T |
|---|---|
| A clean starting pattern for imaging-AI pipelines | A turnkey product or a heavy framework |
| Model-agnostic (bring any model) | Tied to a specific model or vendor |
| A teaching/reference scaffold | Anyone's proprietary pipeline |
| Yours to fork and extend | Medical advice or a regulatory-cleared system |

## Repo layout

```
openmedpipe/
├─ models/       ModelPlugin contract + registry + example models
├─ pipeline/     orchestrator (stage runner)
├─ qc/           quality-control checks
├─ assistant/    optional local-LLM pipeline suggester (Ollama)
└─ web/          minimal submission API stub
containers/      Dockerfile template to wrap a model
examples/        end-to-end demo
docs/            architecture + how-to-extend
```

## License

Apache-2.0 — free for commercial and private use. See [LICENSE](LICENSE).

## Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). If you build something with it, tell us.
