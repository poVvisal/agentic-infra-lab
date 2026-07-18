## Verified

```bash
curl http://localhost:11434/api/generate \
  -d '{"model":"llama3.2","prompt":"Say hello in one sentence.","stream":false}'
```

Expected success condition: JSON includes `"response"`, `"done": true`, and `"done_reason": "stop"`.

Verified locally on 2026-07-18 with model `llama3.2`.