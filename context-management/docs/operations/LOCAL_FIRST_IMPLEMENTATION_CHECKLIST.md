# LOCAL-FIRST IMPLEMENTATION CHECKLIST
## Tactical Guide to HSL Reliability

---

## PHASE 1: DEBUG & ESTABLISH RELIABILITY (Weeks 1-2)

### Week 1: Debug HSL Exit Code 1

- [ ] **Day 1-2: Reproduce Failure**
  - [ ] Run HSL daemon locally with verbose logging
  - [ ] Capture exit code 1 consistently
  - [ ] Record full error message and stack trace
  - [ ] Attempt to reproduce on different machine (if possible)
  - [ ] Document reproduction steps precisely

- [ ] **Day 3: Add Comprehensive Logging**
  - [ ] Add logging at daemon startup
  - [ ] Add logging for each file watch event
  - [ ] Add logging for each event processing step
  - [ ] Add logging before daemon exits
  - [ ] Use structured logging (JSON or similar) for production
  - [ ] Ensure all errors include full context (file, line, state)

- [ ] **Day 4: Identify Root Cause**
  - [ ] Run with full logging
  - [ ] Identify exact line where failure occurs
  - [ ] Check for: missing dependencies, configuration errors, permission issues
  - [ ] Verify all assumptions (file paths exist, permissions correct, etc.)
  - [ ] Document root cause clearly

- [ ] **Day 5: Fix & Verify**
  - [ ] Implement fix for identified root cause
  - [ ] Run daemon continuously for 1 hour
  - [ ] Process >100 file events during test run
  - [ ] Verify exit code = 0 (success)
  - [ ] Commit fix with detailed message

### Week 1-2: Establish Health Metrics

- [ ] **Define Success Metrics**
  - [ ] File events processed within 100ms: Target/Actual
  - [ ] Confidence reports generated within 1 second: Target/Actual
  - [ ] Error rate < 0.1%: Target/Actual
  - [ ] Memory usage stable (no growth over 1 hour): Target/Actual
  - [ ] CPU usage proportional to file event rate: Target/Actual

- [ ] **Add Health Check Endpoint** (if daemon has HTTP interface)
  - [ ] `GET /health` returns JSON with metrics
  - [ ] Metrics include: uptime, events_processed, errors, memory_mb, cpu_percent
  - [ ] Health check passes if all metrics within acceptable range

- [ ] **Create Monitoring Dashboard** (local)
  - [ ] Real-time display of health metrics
  - [ ] Graph of file event processing rate
  - [ ] Graph of report generation latency
  - [ ] Alert thresholds for failures

### Week 2: Build Local Event Loop

- [ ] **File Watcher Implementation**
  - [ ] Watch directory: `src/` (or equivalent)
  - [ ] Detect events: add, change, delete
  - [ ] Handle edge cases: rapid changes, concurrent modifications, chunked writes
  - [ ] Publish events to local queue with unique ID

- [ ] **Event Stream (Local Queue)**
  - [ ] Queue system: Python multiprocessing.Queue OR asyncio.Queue OR Redis (local)
  - [ ] Event format: JSON with timestamp, file_path, event_type
  - [ ] Queue size: Monitor for backlog
  - [ ] Persistence: (Optional, but helpful for replay/debugging)

- [ ] **Confidence System Subscriber**
  - [ ] Subscribe to file events
  - [ ] Process asynchronously (non-blocking)
  - [ ] Publish ANALYSIS_COMPLETE events when done
  - [ ] Handle errors gracefully (retry, log, continue)

- [ ] **Report Generation**
  - [ ] Subscribe to ANALYSIS_COMPLETE events
  - [ ] Generate confidence reports
  - [ ] Store reports to disk with timestamp
  - [ ] Publish REPORT_GENERATED events for consumers

- [ ] **Event Loop Test**
  - [ ] Modify a file in watched directory
  - [ ] Verify: File event → Analysis → Report generated
  - [ ] Check latency end-to-end (target: <2 seconds)
  - [ ] Test rapid successive changes (target: handle 10+ per second)

---

## PHASE 2: ADD TESTING (Week 2-3)

### Unit Tests: Daemon Component

- [ ] **Test: File Watch Detection**
  ```python
  def test_file_watch_detects_add():
      # Create file in watched directory
      # Verify daemon detects add event within 100ms

  def test_file_watch_detects_change():
      # Modify file in watched directory
      # Verify daemon detects change event within 100ms

  def test_file_watch_detects_delete():
      # Delete file in watched directory
      # Verify daemon detects delete event within 100ms
  ```

- [ ] **Test: Event Publishing**
  ```python
  def test_event_has_unique_id():
      # Each event has unique identifier

  def test_event_has_timestamp():
      # Each event has timestamp

  def test_event_has_metadata():
      # Each event has file_path, event_type, etc.
  ```

- [ ] **Test: Error Handling**
  ```python
  def test_handles_permission_denied():
      # File watch continues even if permission denied

  def test_handles_broken_symlink():
      # File watch continues even if symlink broken

  def test_handles_rapid_changes():
      # File watch handles 10+ rapid changes correctly
  ```

### Integration Tests: Daemon + Confidence System

- [ ] **Test: End-to-End File → Report**
  ```python
  def test_file_change_generates_report():
      # 1. Modify file in watched directory
      # 2. Wait for analysis to complete
      # 3. Verify confidence report generated
      # 4. Check report contains correct analysis

  def test_multiple_files_processed_sequentially():
      # 1. Modify file A
      # 2. Wait for report A
      # 3. Modify file B
      # 4. Wait for report B
      # 5. Verify both reports correct
  ```

- [ ] **Test: Concurrent Processing**
  ```python
  def test_handles_concurrent_file_modifications():
      # 1. Modify file A and B simultaneously
      # 2. Verify both analyzed correctly
      # 3. Verify no race conditions
  ```

- [ ] **Test: Event Ordering**
  ```python
  def test_preserves_event_order():
      # 1. Generate 10 file events in sequence
      # 2. Verify processed in same order
      # 3. Verify no reordering
  ```

### Stress Tests: Load & Performance

- [ ] **Test: High File Event Rate**
  ```python
  def test_handles_1000_events_per_second():
      # Generate 1000 file events rapidly
      # Measure: latency, error rate, memory growth
      # Target: <2 second latency, 0 errors, stable memory
  ```

- [ ] **Test: Long-Running Stability**
  ```python
  def test_daemon_stable_for_1_hour():
      # Run daemon for 1 hour with continuous file events
      # Monitor: memory (should not grow), CPU (should be proportional)
      # Verify: zero crashes, zero hangs
  ```

- [ ] **Test: Recovery from Failure**
  ```python
  def test_recovers_after_confidence_crash():
      # 1. Run daemon + confidence system
      # 2. Kill confidence system process
      # 3. Verify daemon continues
      # 4. Restart confidence system
      # 5. Verify events queued during outage are processed
  ```

### Test Infrastructure

- [ ] **Create Test Directory Structure**
  ```
  tests/
  ├── unit/
  │   ├── test_file_watch.py
  │   ├── test_event_publishing.py
  │   └── test_error_handling.py
  ├── integration/
  │   ├── test_end_to_end.py
  │   └── test_event_ordering.py
  └── stress/
      ├── test_high_rate.py
      └── test_stability.py
  ```

- [ ] **Test Runner Configuration**
  ```bash
  # Run all tests
  pytest tests/ -v

  # Run specific category
  pytest tests/unit/ -v
  pytest tests/integration/ -v
  pytest tests/stress/ -v

  # Run with coverage
  pytest tests/ --cov=src --cov-report=html
  ```

- [ ] **CI/CD Integration** (Optional but recommended)
  - [ ] Tests run on every commit
  - [ ] Failures block merge to main
  - [ ] Coverage report generated

---

## PHASE 3: LOCAL STAGING VALIDATION (Week 3-4)

### Create Local Staging Environment

- [ ] **Staging Directory Structure**
  ```
  staging/
  ├── config/
  │   ├── daemon.conf  (production-like config)
  │   └── confidence.conf
  ├── data/
  │   └── (analysis data goes here)
  └── logs/
      └── (structured logs)
  ```

- [ ] **Production Configuration in Staging**
  - [ ] Copy production config to staging/config/
  - [ ] Update paths to point to staging/ instead of /var/lib/
  - [ ] Verify all environment variables set correctly
  - [ ] Verify all secrets/credentials accessible

- [ ] **Staging Runs Test Suite**
  - [ ] Run full test suite in staging environment
  - [ ] Verify tests pass (same as local)
  - [ ] Measure performance metrics in staging
  - [ ] Verify metrics match local development

### Configuration Drift Detection

- [ ] **Identify Configuration Differences**
  ```
  Local Dev Config:
  - Database: SQLite at ./data.db
  - Log level: DEBUG
  - Event queue: In-memory

  Staging Config:
  - Database: PostgreSQL at localhost:5432
  - Log level: INFO
  - Event queue: Redis at localhost:6379

  Question: Do tests pass with BOTH configurations?
  ```

- [ ] **Fix Configuration Drift**
  - [ ] Identify why configs are different
  - [ ] Determine if differences are necessary
  - [ ] Update config management to eliminate unnecessary drift
  - [ ] Document necessary differences

### Performance Baseline in Staging

- [ ] **Measure Key Metrics**
  ```
  Metric                          | Dev | Staging | Target | Status
  ─────────────────────────────────────────────────────────────────
  File event processing latency   | 45ms | 50ms | <100ms  | ✓
  Report generation time          | 800ms | 850ms | <1000ms | ✓
  Memory usage (1 hour run)       | Stable | Stable | No growth | ✓
  Error rate                       | 0 | 0 | <0.1% | ✓
  ```

- [ ] **Test Staging→Production Readiness**
  - [ ] Staging config matches production exactly
  - [ ] Staging metrics pass all thresholds
  - [ ] No drift discovered between staging and production config
  - [ ] All tests pass in staging environment

---

## PHASE 4: PREPARE FOR CLOUD DEPLOYMENT (Week 4)

### Pre-Deployment Checklist

- [ ] **Code Quality**
  - [ ] All tests pass: `pytest tests/ -v`
  - [ ] Code coverage >80%: `pytest tests/ --cov`
  - [ ] No warnings: `python -m pylint src/ --fail-under=8.0`
  - [ ] Type hints complete: `mypy src/`

- [ ] **Documentation**
  - [ ] README explains how to run locally
  - [ ] Architecture documented in `ARCHITECTURE.md`
  - [ ] Configuration documented in `CONFIG.md`
  - [ ] Troubleshooting guide in `TROUBLESHOOTING.md`

- [ ] **Health Metrics Validated**
  - [ ] File event processing: <100ms ✓
  - [ ] Report generation: <1 second ✓
  - [ ] Error rate: <0.1% ✓
  - [ ] Memory: Stable ✓
  - [ ] CPU: Proportional ✓

- [ ] **Deployment Artifacts**
  - [ ] Dockerfile created and tested locally
  - [ ] Docker image builds successfully
  - [ ] Docker image runs successfully
  - [ ] Health check endpoint works in Docker

- [ ] **Monitoring & Observability**
  - [ ] Structured logging implemented (JSON)
  - [ ] Log aggregation tested locally
  - [ ] Metrics exported (Prometheus/StatsD/CloudMonitoring)
  - [ ] Alerting thresholds defined

### Cloud Deployment Plan

- [ ] **Create Deployment Documentation**
  ```
  CLOUD_DEPLOYMENT.md
  ├── Prerequisites (credentials, project setup)
  ├── Deployment Steps
  ├── Configuration (environment variables, secrets)
  ├── Health Check Procedure
  ├── Rollback Procedure (if deployment fails)
  └── Post-Deployment Validation
  ```

- [ ] **Define Success Criteria for Cloud**
  - [ ] Health checks pass
  - [ ] Metrics accessible and in-range
  - [ ] No errors in logs during 1-hour bake time
  - [ ] Manual smoke test succeeds

- [ ] **Define Failure Criteria**
  - [ ] If health checks fail → immediate rollback
  - [ ] If error rate >1% → investigate
  - [ ] If latency >2 seconds → investigate
  - [ ] If memory growing → investigate and rollback

---

## VALIDATION GATES: APPROVAL TO PROCEED

### Must Clear Before Proceeding to Next Phase

**Gate 1 → Phase 2 (Testing):**
- [ ] HSL daemon runs continuously without exit code 1
- [ ] Daemon can process 100+ file events
- [ ] All health metrics measured and logged
- [ ] Root cause of original failure documented

**Gate 2 → Phase 3 (Staging):**
- [ ] All unit tests pass (>20 tests)
- [ ] All integration tests pass (>10 tests)
- [ ] Code coverage >80%
- [ ] No regressions from original code

**Gate 3 → Phase 4 (Cloud Prep):**
- [ ] Staging environment matches dev environment behavior exactly
- [ ] All metrics stable in staging
- [ ] No configuration drift discovered
- [ ] Performance metrics meet or exceed targets

**Gate 4 → Cloud Deployment:**
- [ ] All code quality checks pass
- [ ] All tests pass in staging
- [ ] Documentation complete
- [ ] Docker image built, tested, verified
- [ ] Health checks work
- [ ] Deployment plan documented
- [ ] Rollback plan documented

---

## DAILY STANDUP TEMPLATE

**When:** 9 AM each day
**Duration:** 15 minutes
**What to Report:**

```
Date: 2026-01-24
Phase: 1 (Debug & Establish)

Today's Progress:
- [ ] What was accomplished yesterday
- [ ] What metrics improved
- [ ] What blockers were discovered

Blockers:
- [ ] List any issues preventing progress
- [ ] What support is needed

Tomorrow's Focus:
- [ ] Specific tasks planned for today
- [ ] What milestone we're targeting

Health Metrics (Latest):
- File event latency: 45ms (target: <100ms) ✓
- Report generation: 800ms (target: <1s) ✓
- Error rate: 0% (target: <0.1%) ✓
- Memory: Stable (no growth) ✓
```

---

## SUCCESS CRITERIA: WHEN TO DECLARE "READY FOR CLOUD"

- [ ] **Exit Code 1 Resolved:** Daemon runs continuously, no failures
- [ ] **Event Loop Working:** File → Event → Analysis → Report (end-to-end)
- [ ] **Testing Comprehensive:** >30 tests, all passing, >80% coverage
- [ ] **Performance Baseline:** All metrics within targets locally AND in staging
- [ ] **Configuration Consistent:** No drift between dev and staging
- [ ] **Documentation Complete:** How to build, deploy, troubleshoot
- [ ] **Deployment Artifacts:** Docker image built, tested, verified
- [ ] **Health Monitoring:** Metrics and alerts configured
- [ ] **Team Agreement:** Leadership confirms ready to proceed

---

## ESTIMATED TIMELINE

| Phase | Duration | Milestones |
|-------|----------|-----------|
| Phase 1: Debug | 2 weeks | Exit code 1 resolved, health metrics established |
| Phase 2: Testing | 1 week | >30 tests passing, >80% coverage |
| Phase 3: Staging | 1 week | Config validated, metrics confirmed |
| Phase 4: Cloud Prep | 1 week | Docker image, deployment plan ready |
| **Total** | **4-5 weeks** | **Ready for production cloud deployment** |

---

## RISK MITIGATION

**Risk: Timeline Slips**
- Mitigation: Daily standups, weekly progress reviews, escalate blockers immediately

**Risk: Unforeseen Issues Discovered in Testing**
- Mitigation: Have buffer week built into timeline, fix issues immediately

**Risk: Configuration Drift Discovered Late**
- Mitigation: Compare config files daily, catch drift early

**Risk: Team Pressure to Skip Stages**
- Mitigation: Reference this document, show cost data ($3M per incident), hold firm

---

## WHO OWNS WHAT

| Task | Owner | Approval |
|------|-------|----------|
| Debug & Fix HSL | HSL Lead | HSL Lead |
| Event Loop | HSL Lead | Tech Lead |
| Unit Testing | QA Engineer | QA Lead |
| Integration Testing | QA Engineer | QA Lead |
| Staging Setup | Infrastructure | Tech Lead |
| Docker/Deployment | Infrastructure | Tech Lead |
| Documentation | Tech Writer | Product Manager |
| Final Approval | Tech Lead | Engineering Manager |

---

## DOCUMENT REFERENCES

- **Case Analysis:** `CASE_AGAINST_PREMATURE_CLOUD.md`
- **Decision Brief:** `DECISION_BRIEF_LOCAL_FIRST.md`
- **Research (Full):** `standard-model-of-code/docs/research/perplexity/docs/20260123_113658_*`

---

**Last Updated:** 2026-01-23
**Status:** ACTIVE - Following this checklist
**Next Review:** After Phase 1 completion (Week 2)
