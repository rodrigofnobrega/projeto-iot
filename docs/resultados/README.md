# Resultados dos Testes

Os arquivos `.md` desta pasta são **gerados automaticamente** ao executar a
suíte de testes:

```bash
cd ../../tests
python3 run_tests.py
```

Cada teste cria seu próprio relatório (`test_latency.md`, `test_multi_client.md`,
`test_reconnect.md`) com **data, parâmetros e conclusão**, e o runner gera o
`_resumo.md` com a visão geral da execução.

> Esta pasta começa vazia (apenas este README) até a primeira execução.
