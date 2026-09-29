# Publish checklist

Public GitHub project: **https://github.com/aegis-red/aegis-red**  
Copyright: **rfintek Inc.** (Apache-2.0). GitHub org and repo: **aegis-red** (product brand; company name is not in the URL).

After the first push:

1. Settings → General: topics `ai-safety`, `llm`, `agents`, `assurance`. Description: authorized AI-agent assurance harness.
2. Settings → Code security: enable private vulnerability reporting and Dependabot alerts.
3. Open the issues in `docs/LAUNCH_ISSUES.md`. Label `good first issue`.
4. Tag `v0.1.0` after CI is green.
5. Do not upload `data/evidence/` or production transcripts.

Clone:

```bash
git clone https://github.com/aegis-red/aegis-red.git
cd aegis-red
```
