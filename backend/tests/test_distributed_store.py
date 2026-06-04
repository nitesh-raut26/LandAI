"""Distributed-state validation — HONEST scope.

These tests drive the REAL Redis code path in app.store via ``fakeredis`` and
prove shared-state correctness across replicas (a denylist/quota written by one
client is visible to another client on the same server). That validates the
*logic* that makes auth revocation and quota fair across nodes.

What this does NOT do (and we don't pretend it does): exercise a real multi-host
Redis cluster, failover, or network partitions. Those require a deployed cluster
and are documented as the remaining production-validation step.
"""
import uuid

import fakeredis
from fastapi.testclient import TestClient

from app import store
from app.main import app

client = TestClient(app)


def _fake():
    return fakeredis.FakeStrictRedis(decode_responses=True)


def test_redis_code_path_counter_denylist_rate():
    store.use_redis(_fake())
    try:
        assert store.backend_name() == "redis" and store.is_distributed() is True
        # counters
        assert store.incr("c", 1, ttl=60) == 1
        assert store.incr("c", 1) == 2
        assert store.get_int("c") == 2
        # denylist
        store.mark("dl:fam:x", 60)
        assert store.is_marked("dl:fam:x") is True
        store.delete("dl:fam:x")
        assert store.is_marked("dl:fam:x") is False
        # fixed-window rate (limit 2)
        ok1, rem1 = store.rate_allow("rl:key:1", 2, 60)
        store.rate_allow("rl:key:1", 2, 60)
        ok3, rem3 = store.rate_allow("rl:key:1", 2, 60)
        assert ok1 is True and rem1 == 1
        assert ok3 is False and rem3 == 0
    finally:
        store.use_redis(None)


def test_cross_replica_shared_state():
    server = fakeredis.FakeServer()
    a = fakeredis.FakeStrictRedis(server=server, decode_responses=True)
    b = fakeredis.FakeStrictRedis(server=server, decode_responses=True)
    try:
        store.use_redis(a)
        store.mark("dl:fam:shared", 60)            # replica A revokes a token family
        store.incr("quota:key:9", 1, ttl=86400)    # replica A consumes quota
        store.use_redis(b)                          # switch to replica B (same server)
        assert store.is_marked("dl:fam:shared") is True   # B sees the revocation
        assert store.get_int("quota:key:9") == 1          # B sees the quota usage
    finally:
        store.use_redis(None)


def test_auth_revocation_works_through_redis_path():
    """End-to-end: logout denylists the family in (fake) Redis → access token dies."""
    store.use_redis(_fake())
    try:
        email = f"r{uuid.uuid4().hex[:8]}@example.com"
        reg = client.post("/api/auth/register", json={"email": email, "password": "supersecret1"}).json()
        h = {"Authorization": f"Bearer {reg['access_token']}"}
        assert client.get("/api/auth/me", headers=h).status_code == 200
        client.post("/api/auth/logout", json={"refresh_token": reg["refresh_token"]})
        assert client.get("/api/auth/me", headers=h).status_code == 401   # revoked via Redis
        assert client.get("/api/system/metrics").json()["shared_state_backend"] == "redis"
    finally:
        store.use_redis(None)
