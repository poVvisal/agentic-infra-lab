package com.agentlab.agentservice.controller;

import com.agentlab.agentservice.service.AgentService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class AgentController {

    private final AgentService agentService;

    public AgentController(AgentService agentService) {
        this.agentService = agentService;
    }

    @PostMapping("/chat")
    public ChatResponse chat(@RequestBody ChatRequest request) {
        String reply = agentService.getResponse(request.prompt());
        return new ChatResponse(reply);
    }

    public record ChatRequest(String prompt) {}
    public record ChatResponse(String response) {}
}