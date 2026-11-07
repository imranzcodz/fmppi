# Progress Tracking & Resume

## How to Check Progress
- `git log --oneline -10` — last committed work
- `git status` — uncommitted/working-tree state
- `git branch --show-current` — active branch (`develop` = integration)
- Sprint board (Jira/Linear): story states To Do / In Progress / Review / Done
- Burndown chart: points remaining vs ideal per sprint
- MLflow UI: last experiment runs, metrics, model versions
- CI/CD: GitHub Actions run status for `develop`/`main`

## Identifying Last State
Check these in order:
1. Branch: should be `develop` (or feature branch `feat/<agent>/<topic>`)
2. Last commit: message + files changed → tells what was last built
3. Uncommitted changes: `git status` → half-finished work
4. Story board: last story moved to "Done" / "Review"
5. Quality gates: last sprint gate sign-off (G1–G6)
6. MLflow: latest trained model + metrics vs thresholds
7. Deploy: last successful CI run / staging deployment

## Resume Point (Definition)
Resume from the last **Done** story that meets DoD:
- code reviewed + merged to `develop`
- tests passing in CI
- docs updated
- deployed to staging (if applicable)

## Resume Checklist
1. `git checkout develop && git pull`
2. `git status` → stash or commit any half-work
3. Pick highest-priority To Do story matching agent scope
4. Create feature branch `feat/<agent>/<topic>`
5. Implement → tests → lint/typecheck → PR → merge to `develop`
6. Update sprint board + burndown
7. Log MLflow run if ML work; update model registry if promoted
8. Mark story Done; review quality gates

## Checkpoint Manifest (`CHECKPOINT.json` — maintain manually)
- lastCommit, branch, sprint, storyDone, mlflowRunId, modelVersion, deployEnv, gateSignOff
- Update at end of each work session so any agent can resume precisely.
