kingczin@DESKTOP-L6STR70:/mnt/c/Users/kingczin/Desktop/agentic-infra-lab$ curl -X POST http://localhost:8080/api/chat \
-H "Content-Type: application/json" \
-d '{"prompt": "Say hello in one sentence."}'
{"response":"Hello, how are you today?"}kingczin@DESKTOP-L6STR70:/mnt/c/Users/kingczin/Desktop/agentic-infra-lab$
kingczin@DESKTOP-L6STR70:/mnt/c/Users/kingczin/Desktop/agentic-infra-lab$
kingczin@DESKTOP-L6STR70:/mnt/c/Users/kingczin/Desktop/agentic-infra-lab$ curl -X POST http://localhost:8080/api/chat   -H "Content-Type: application/json"   -d '{"prompt": "Say hello in one sentence."}'
{"response":"Hello, how can I assist you today?"}kingczin@DESKTOP-L6STR70:/mnt/c/Users/kingczin/Desktop/agentic-infra-lab$
