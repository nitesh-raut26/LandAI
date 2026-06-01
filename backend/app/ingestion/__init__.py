"""
LAND AI — Real Data Ingestion Layer
===================================

This package turns LAND AI from a *curated* dataset into a platform that
ingests **real, continuously-refreshable, legally-sourced** intelligence.

Core promise (the data contract)
---------------------------------
Every dataset that enters the platform is wrapped in a
:class:`~app.ingestion.provenance.Provenance` envelope that records:

    source · source_url · license · fetched_at · confidence ·
    freshness_score · legality_note

Nothing is invented. Nothing is randomly generated. If a source is unavailable
we return an explicit "unavailable" envelope — never fabricated numbers.

Compliance
----------
External access is mediated by :mod:`app.ingestion.compliance`. Sources whose
Terms of Service prohibit automated access (e.g. listing portals) are registered
with ``allowed=False`` and their adapters **refuse to run**. Web sources are
additionally checked against ``robots.txt`` before any fetch.

Sub-packages
------------
- ``scrapers``    — source adapters (Overpass, Nominatim, gated listing stub)
- ``normalizers`` — raw payload → canonical schema
- ``enrichers``   — derived geo-economic features (distances, density scores)
- ``pipelines``   — orchestration (city → adapters → normalize → enrich → envelope)
"""
