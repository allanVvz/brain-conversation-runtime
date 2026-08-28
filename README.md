# brain-conversation-runtime

Decisao, GraphRAG, ledger, proof, journeys, qualificacao, agents e WA Validator.
Extraido de `brain-plataform` no SHA `b6ee5edc884e233cc0ff41798f4c19239e04fd88`.

Deploy nao executa migrations. Readiness exige schema minimo 131 e `BRAIN_DB_JWT`
com claim `role=brain_runtime`; `service_role` e recusada. Endpoints internos
ficam sob `/internal/v1/*` e exigem `AI_BRAIN_WEBHOOK_TOKEN`.
