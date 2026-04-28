from __future__ import annotations

import logging
import math
from src.models import Asset
from src.models import AssetConfig
from src.models import ASSET_CONFIGS
from src.models import PriorityTier
from src.models import ScoredAsset


logger = logging.getLogger(__name__)

_THRESHOLD_P1 = 0.50   # ~top 10% of assets
_THRESHOLD_P2 = 0.35   # ~next 20%
_THRESHOLD_P3 = 0.20   # ~next 30%


def compute_pof(asset: Asset) -> float:
    age_factor       = min(asset.age_ratio, 1.0)
    condition_factor = (10 - asset.inspection_score) / 9
    fault_factor     = min(asset.fault_count_5yr / 5, 1.0)

    return round(
        0.5 * age_factor + 0.3 * condition_factor + 0.2 * fault_factor,
        4,
    )


def compute_cof(asset: Asset) -> float:
    customer_factor = math.log1p(asset.customers_affected_if_fail) / math.log1p(2000)
    critical_factor = 1.0 if asset.is_critical_node else 0.3
    cost_factor     = math.log1p(asset.replacement_cost_nzd) / math.log1p(500_000)

    return round(
        0.5 * customer_factor + 0.3 * critical_factor + 0.2 * cost_factor,
        4,
    )


def assign_tier(risk_score: float) -> PriorityTier:
    if risk_score >= _THRESHOLD_P1:
        return PriorityTier.P1_CRITICAL
    elif risk_score >= _THRESHOLD_P2:
        return PriorityTier.P2_HIGH
    elif risk_score >= _THRESHOLD_P3:
        return PriorityTier.P3_MEDIUM
    return PriorityTier.P4_LOW


def score_asset(asset: Asset) -> ScoredAsset:
    pof   = compute_pof(asset)
    cof   = compute_cof(asset)
    risk  = round(pof * cof, 4)
    tier  = assign_tier(risk)
    return ScoredAsset(asset=asset, pof_score=pof, cof_score=cof,
                       risk_score=risk, priority_tier=tier)


def score_all(assets: list[Asset]) -> list[ScoredAsset]:
    scored = [score_asset(a) for a in assets]
    p1_count = sum(1 for s in scored if s.priority_tier == PriorityTier.P1_CRITICAL)
    logger.info(f"Scored {len(scored)} assets. P1 Critical: {p1_count}")
    return scored