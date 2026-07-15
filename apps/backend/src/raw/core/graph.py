"""The LangGraph graph — State + Nodes + Edges, checkpointed to Postgres.

TODO (Sprint 0.5): build the graph wrapping core/loop.py:
  - nodes: agent (call model), tools (execute), error-handler
  - conditional edge: should_continue -> tools | end (iteration cap)
  - PostgresSaver checkpointer (externalized state -> resumable + scalable)
"""
