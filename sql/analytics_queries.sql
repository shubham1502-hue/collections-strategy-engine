-- ============================================================
-- Collections Contact Strategy Engine — SQL Analytics
-- ============================================================
-- These queries run on the ab_test_results table (load
-- outputs/tableau_master.csv into your SQL client or DuckDB).
--
-- Usage (DuckDB CLI):
--   duckdb
--   > CREATE TABLE ab AS SELECT * FROM read_csv_auto('outputs/tableau_master.csv');
--   > .read sql/analytics_queries.sql
-- ============================================================


-- ── 1. Overall A/B Test Summary ──────────────────────────────────────────────
SELECT
    arm,
    COUNT(*)                                                  AS total_borrowers,
    SUM(responded)                                            AS total_responded,
    ROUND(SUM(responded) * 100.0 / COUNT(*), 2)               AS response_rate_pct,
    ROUND(SUM(amount_recovered), 0)                           AS total_recovered,
    ROUND(SUM(amount_recovered) / COUNT(*), 2)                AS avg_recovery_per_borrower,
    ROUND(SUM(amount_recovered) / NULLIF(SUM(responded), 0), 2) AS recovery_per_response
FROM ab
GROUP BY arm
ORDER BY arm;


-- ── 2. Recovery Lift Calculation ─────────────────────────────────────────────
WITH arms AS (
    SELECT
        arm,
        ROUND(SUM(responded) * 100.0 / COUNT(*), 2)  AS response_rate,
        ROUND(SUM(amount_recovered), 0)               AS total_recovered
    FROM ab
    GROUP BY arm
)
SELECT
    t.response_rate - c.response_rate               AS response_rate_lift_pp,
    ROUND((t.total_recovered - c.total_recovered)
          / c.total_recovered * 100, 2)             AS recovery_lift_pct,
    t.total_recovered - c.total_recovered           AS incremental_recovery
FROM arms t
JOIN arms c ON t.arm = 'Treatment' AND c.arm = 'Control';


-- ── 3. Recovery by DPD Bucket and Arm ────────────────────────────────────────
SELECT
    arm,
    dpd_bucket,
    COUNT(*)                                            AS borrowers,
    SUM(responded)                                      AS responded,
    ROUND(SUM(responded) * 100.0 / COUNT(*), 2)         AS response_rate_pct,
    ROUND(SUM(amount_recovered), 0)                     AS total_recovered,
    ROUND(SUM(amount_recovered) / COUNT(*), 2)          AS avg_recovered_per_borrower
FROM ab
GROUP BY arm, dpd_bucket
ORDER BY dpd_bucket, arm;


-- ── 4. Channel Performance (Treatment Arm) ────────────────────────────────────
SELECT
    strategy_channel,
    COUNT(*)                                            AS borrowers,
    SUM(responded)                                      AS responded,
    ROUND(SUM(responded) * 100.0 / COUNT(*), 2)         AS response_rate_pct,
    ROUND(SUM(amount_recovered), 0)                     AS total_recovered,
    ROUND(SUM(amount_recovered) / COUNT(*), 2)          AS recovery_per_contact
FROM ab
WHERE arm = 'Treatment'
GROUP BY strategy_channel
ORDER BY response_rate_pct DESC;


-- ── 5. Offer Effectiveness ────────────────────────────────────────────────────
SELECT
    arm,
    strategy_offer,
    COUNT(*)                                            AS borrowers,
    ROUND(SUM(responded) * 100.0 / COUNT(*), 2)         AS response_rate_pct,
    ROUND(SUM(amount_recovered) / COUNT(*), 2)          AS avg_recovery_per_borrower
FROM ab
GROUP BY arm, strategy_offer
ORDER BY arm, avg_recovery_per_borrower DESC;


-- ── 6. Pareto: Top Segments by Recovery ──────────────────────────────────────
WITH seg AS (
    SELECT
        dpd_bucket,
        risk_tier,
        COUNT(*)                                        AS borrowers,
        ROUND(SUM(amount_recovered), 0)                 AS total_recovered
    FROM ab
    WHERE arm = 'Treatment'
    GROUP BY dpd_bucket, risk_tier
),
total AS (SELECT SUM(total_recovered) AS grand_total FROM seg)
SELECT
    s.dpd_bucket,
    s.risk_tier,
    s.borrowers,
    s.total_recovered,
    ROUND(s.total_recovered * 100.0 / t.grand_total, 2)  AS share_pct,
    ROUND(SUM(s2.total_recovered * 100.0 / t.grand_total)
          OVER (ORDER BY s.total_recovered DESC), 2)      AS cumulative_pct
FROM seg s
CROSS JOIN total t
JOIN seg s2 ON s2.total_recovered <= s.total_recovered OR s2.dpd_bucket = s.dpd_bucket
GROUP BY s.dpd_bucket, s.risk_tier, s.borrowers, s.total_recovered, t.grand_total
ORDER BY s.total_recovered DESC
LIMIT 10;


-- ── 7. Timing Window Effectiveness ───────────────────────────────────────────
SELECT
    strategy_window,
    COUNT(*)                                            AS borrowers,
    ROUND(SUM(responded) * 100.0 / COUNT(*), 2)         AS response_rate_pct,
    ROUND(SUM(amount_recovered) / COUNT(*), 2)          AS recovery_per_contact
FROM ab
WHERE arm = 'Treatment'
GROUP BY strategy_window
ORDER BY response_rate_pct DESC;


-- ── 8. Risk Tier Breakdown ────────────────────────────────────────────────────
SELECT
    arm,
    risk_tier,
    COUNT(*)                                            AS borrowers,
    ROUND(SUM(responded) * 100.0 / COUNT(*), 2)         AS response_rate_pct,
    ROUND(SUM(amount_recovered), 0)                     AS total_recovered
FROM ab
GROUP BY arm, risk_tier
ORDER BY risk_tier, arm;
