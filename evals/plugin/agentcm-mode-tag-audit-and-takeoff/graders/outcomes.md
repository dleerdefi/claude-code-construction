---
type: llm

weight: 1
---
The final message reports what AgentCM answered for the tags it sent (how many were created, already held, rejected or had no free text), taken from AgentCM's answer, not assumed from the request succeeding. If AgentCM answered that the PE rejected a tag, that tag is listed apart and not counted; a run with no rejected tag passes this on the rest.
