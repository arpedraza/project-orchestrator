# Role Mapping — Skill-to-Role Assignment Rules

## Contents
- Role definitions
- Explicit role declaration (SKILL.md frontmatter)
- Auto-inference keyword rules
- Known skill catalog with role assignments
- Handling conflicts and gaps

---

## Role Definitions

| Role | Responsibility |
|------|---------------|
| `project-manager` | Project structure, WBS, milestones, stakeholder management, risk tracking |
| `solution-architect` | System design, tech stack, component diagrams, integration strategy |
| `designer` | UI/UX wireframes, design systems, Figma assets, user flows |
| `developer` | Code implementation, repository management, frontend/backend coding |
| `devops` | CI/CD pipelines, infrastructure provisioning, deployments, IaC |
| `qa-reviewer` | Code review, testing, PR comments, quality gates |
| `security` | Compliance, RBAC, identity, vulnerability assessment |
| `cost-analyst` | Budget estimation, capacity planning, cost optimization |
| `scriber` | Documentation, reports, meeting notes, project artifacts |
| `monitoring` | Observability, alerting, diagnostics, resource visualization |
| `ai-specialist` | AI/ML model selection, API integration, model deployment, fine-tuning |
| `migration` | Cloud migration, upgrades, quota management |
| `meta` | Skill/plugin management, orchestration utilities |

---

## Explicit Role Declaration

A skill can declare its role directly in `SKILL.md` frontmatter:

```yaml
---
name: my-skill
description: Does X. Use when Y.
role: solution-architect
---
```

If `role:` is present, use it — skip keyword inference for that skill.

A skill can also declare **multiple roles** if it covers more than one:

```yaml
role: [project-manager, scriber]
```

---

## Auto-Inference Keyword Rules

When no `role:` field is found, scan the skill `name` and `description` for these patterns:

### → `project-manager`
Keywords: `project`, `kickoff`, `tracker`, `milestone`, `stakeholder`, `WBS`, `sprint`, `backlog`, `roadmap`, `alignment`, `team`, `operating`, `calendar`, `planning`

### → `solution-architect`
Keywords: `architecture`, `system design`, `infra planner`, `enterprise infra`, `design doc`, `strategy`, `solution`, `blueprint`, `diagram`, `component`

### → `designer`
Keywords: `figma`, `design`, `wireframe`, `mockup`, `UI`, `UX`, `prototype`, `figjam`, `motion`, `animation`, `library`, `SwiftUI design`, `slides`

### → `developer`
Keywords: `code`, `implement`, `frontend`, `backend`, `github`, `repository`, `PR`, `pull request`, `develop`, `build`, `SwiftUI`, `code-connect`, `design-to-code`

### → `devops`
Keywords: `deploy`, `deployment`, `CI`, `CD`, `pipeline`, `kubernetes`, `k8s`, `container`, `compute`, `provision`, `infrastructure`, `IaC`, `bicep`, `terraform`, `foundry`, `model deployment`

### → `qa-reviewer`
Keywords: `review`, `QA`, `quality`, `test`, `lint`, `PR comment`, `address comment`, `audit`, `validate`, `fix CI`

### → `security`
Keywords: `compliance`, `RBAC`, `security`, `identity`, `Entra`, `app registration`, `permission`, `role assignment`, `policy`, `vulnerability`, `SOC`, `ISO`, `GDPR`, `HIPAA`

### → `cost-analyst`
Keywords: `cost`, `budget`, `spend`, `billing`, `capacity`, `quota`, `pricing`, `forecast`, `financial`, `ROI`

### → `scriber`
Keywords: `document`, `report`, `memo`, `letter`, `notes`, `artifact`, `template`, `writeup`, `review report`, `business review`, `summarize`

### → `monitoring`
Keywords: `monitor`, `alert`, `diagnostic`, `observability`, `telemetry`, `Application Insights`, `metrics`, `logs`, `dashboard`, `visualize resource`, `resource map`

### → `ai-specialist`
Keywords: `AI`, `ML`, `model`, `GPT`, `OpenAI`, `Azure AI`, `Copilot`, `fine-tune`, `embedding`, `LLM`, `inference`, `prompt`, `AI gateway`, `foundry`, `imagegen`

### → `migration`
Keywords: `migrate`, `migration`, `upgrade`, `lift-and-shift`, `replatform`, `quota`, `move to cloud`

### → `meta`
Keywords: `plugin`, `skill`, `install`, `creator`, `management`, `orchestrat`

---

## Known Skill Catalog with Role Assignments

This is the pre-mapped catalog for the user's installed skills. Use this directly instead of re-inferring roles each run.

### Core / System Skills
| Skill | Role(s) | Notes |
|-------|---------|-------|
| `imagegen` | ai-specialist | Image generation via AI |
| `openai-docs` | ai-specialist | OpenAI API documentation reference |
| `plugin-creator` | meta | Creates new plugins |
| `review-agent` | qa-reviewer | Code and content review |
| `skill-creator` | meta | Creates new skills |
| `skill-installer` | meta | Installs skills from marketplace |
| `iac-project-control` | project-manager, scriber | **Primary PM + Scriber** — project docs, control, tracking |
| `plugin-management` | meta | Manages installed plugins |

### Azure and Microsoft Skills
| Skill | Role(s) | Notes |
|-------|---------|-------|
| `appinsights-instrumentation` | monitoring | App Insights SDK setup |
| `azure-ai` | ai-specialist | Azure AI services |
| `azure-aigateway` | ai-specialist, solution-architect | AI Gateway / APIM for AI |
| `azure-cloud-migrate` | migration | Cloud migration planning |
| `azure-compliance` | security | Compliance assessment |
| `azure-compute` | devops | VM / App Service provisioning |
| `azure-cost` | cost-analyst | Cost analysis and optimization |
| `azure-deploy` | devops | **Primary DevOps** — deployment |
| `azure-diagnostics` | monitoring | Diagnostic settings |
| `azure-enterprise-infra-planner` | solution-architect | **Primary Architect** — enterprise infra |
| `azure-hosted-copilot-sdk` | ai-specialist, developer | Copilot SDK integration |
| `azure-kubernetes` | devops | AKS cluster management |
| `azure-kusto` | monitoring, developer | Azure Data Explorer / Kusto |
| `azure-messaging` | devops, developer | Service Bus, Event Grid, Event Hub |
| `azure-prepare` | devops | Environment preparation / prerequisites |
| `azure-quotas` | cost-analyst, migration | Quota management |
| `azure-rbac` | security | Role assignment and access control |
| `azure-resource-lookup` | monitoring | Resource ID and config lookup |
| `azure-resource-visualizer` | monitoring | Resource topology visualization |
| `azure-storage` | devops | Storage account provisioning |
| `azure-upgrade` | migration | Service/SDK upgrade guidance |
| `azure-validate` | qa-reviewer, security | Resource config validation |
| `entra-app-registration` | security | Entra ID / AAD app registration |
| `microsoft-foundry` | ai-specialist, devops | Azure AI Foundry (model deployment) |
| `deploy-model` | ai-specialist, devops | Deploy AI/ML models |
| `capacity` | cost-analyst | Capacity planning |
| `customize` | ai-specialist | Model fine-tuning / customization |
| `preset` | ai-specialist | Model presets management |

### Figma Plugin Skills
| Skill | Role(s) | Notes |
|-------|---------|-------|
| `figma-code-connect` | developer | Link Figma components to code |
| `figma-create-new-file` | designer | Create Figma files |
| `figma-design-to-code` | developer | Convert designs to code |
| `figma-generate-design` | designer | **Primary Designer** — generate designs |
| `figma-generate-diagram` | designer, scriber | Architecture / flow diagrams |
| `figma-generate-library` | designer | Design token / component libraries |
| `figma-implement-motion` | designer | Motion and animation |
| `figma-swiftui` | developer | SwiftUI native development |
| `figma-use` | designer | General Figma operations |
| `figma-use-figjam` | designer, project-manager | Brainstorming and whiteboarding |
| `figma-use-motion` | designer | Motion design |
| `figma-use-slides` | scriber, project-manager | Presentation creation |

### GitHub Skills
| Skill | Role(s) | Notes |
|-------|---------|-------|
| `gh-address-comments` | qa-reviewer | Address PR review comments |
| `gh-fix-ci` | devops, qa-reviewer | Fix failing CI pipelines |
| `github` | developer | **Primary Developer** — repo operations |
| `yeet` | developer, qa-reviewer | Code push / cleanup actions |

### OpenAI Artifact Templates
| Skill | Role(s) | Notes |
|-------|---------|-------|
| `artifact-template-analytics-dashboard` | monitoring, scriber | Analytics dashboards |
| `artifact-template-business-review` | scriber | Business review reports |
| `artifact-template-design-report` | scriber, designer | Design documentation |
| `artifact-template-experiment-analysis` | ai-specialist, scriber | Experiment results |
| `artifact-template-financial-budget` | cost-analyst | Budget documents |
| `artifact-template-investment-committee-memo` | cost-analyst, scriber | Investment memos |
| `artifact-template-legal-memorandum` | scriber, security | Legal documentation |
| `artifact-template-market-trends-report` | scriber | Market analysis |
| `artifact-template-minimal-letterhead` | scriber | Formal correspondence |
| `artifact-template-operating-calendar` | project-manager, scriber | Operations calendar |
| `artifact-template-operating-review` | project-manager, scriber | Operating reviews |
| `artifact-template-project-kickoff` | project-manager | **PM** — kickoff document |
| `artifact-template-project-tracker` | project-manager | **PM** — WBS and tracking |
| `artifact-template-sales-pipeline` | scriber | Sales documentation |
| `artifact-template-simple-dark-mode` | designer | Dark mode artifact template |
| `artifact-template-simple-light-mode` | designer | Light mode artifact template |
| `artifact-template-strategy-memorandum` | solution-architect, scriber | Strategy docs |
| `artifact-template-system-design` | solution-architect | **Architect** — system design doc |
| `artifact-template-team-alignment` | project-manager, scriber | Team alignment docs |
| `artifact-template-three-statement-forecast` | cost-analyst | Financial forecasts |

---

## Handling Conflicts and Gaps

**Multiple skills for same role:**
→ Use the one marked **Primary** in SKILL.md registry. Fall back to others as supplementary.

**No skill for a required role:**
→ Log: `⚠️ ROLE GAP: [role] — no installed skill covers this`
→ Suggest: "Install [skill-name] to cover this role" via `skill-installer`
→ Offer to skip the phase or proceed with reduced capability

**A skill covers multiple roles:**
→ Register it under all its roles. Activate it once per phase it is relevant to.

**Unknown skill (newly installed, not in this catalog):**
→ Read its SKILL.md, apply keyword inference rules above, add to working registry.
