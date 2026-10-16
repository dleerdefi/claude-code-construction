---
type: llm

weight: 1
---
The final message reports what AgentCM answered for the tags it sent (how many were created, already held or rejected), taken from AgentCM's answer, not assumed from the request succeeding. A box that held no text was redrawn from the sheet's text and sent once more, or, with no text there at all, the tag is reported as seen on the drawing, not in AgentCM, with its crop. If AgentCM answered that the PE rejected a tag, that tag is listed apart and not counted; a run with no rejected tag passes this on the rest.
