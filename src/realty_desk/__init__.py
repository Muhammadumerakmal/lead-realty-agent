"""Realty Desk — inquiry triage agent.

One raw client message in; a typed :class:`~realty_desk.schemas.LeadTriage`
verdict out, checked against private inventory and agent availability through
tools. The callback / save decision is made by Python, not the model.

Entry point: ``realty_desk.main:main`` (exposed as the ``realty-desk`` script).
"""
