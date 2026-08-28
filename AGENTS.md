# AGENTS.md

- Ownership: ledger, journeys, proofs, qualificação e estado conversacional.
- Não importar código de outro serviço; somente `brain-contracts` em tag exata.
- Não executar migrations em deploy e não usar service-role universal.
- Um inbound canônico produz no máximo uma decisão e um outbound proof-gated.
- E2E usa WA Validator direto/interno, nunca WhatsApp real.
