from enum import Enum
from dataclasses import dataclass

class AssetType(str, Enum):
    OH_LINE     = "OH_Line"
    UG_CABLE    = "UG_Cable"
    TRANSFORMER = "Transformer"
    SWITCHGEAR  = "Switchgear"
    SUBSTATION  = "Substation"

class PriorityTier(str, Enum):
    P1_CRITICAL = "P1_Critical"
    P2_HIGH     = "P2_High"
    P3_MEDIUM   = "P3_Medium"
    P4_LOW      = "P4_Low"

@dataclass(slots=True)
class Asset:
    asset_id:                    str
    asset_type:                  AssetType
    install_year:                int
    age_years:                   int
    age_ratio:                   float   # age / design_lifespan
    zone:                        str
    voltage_kv:                  int
    customers_affected_if_fail:  int
    last_inspection_year:        int
    inspection_score:            int     # From 1 to 10 1=Critical defects, 10=All good
    fault_count_5yr:             int
    is_critical_node:            bool
    replacement_cost_nzd:        int

@dataclass(slots=True, frozen=True)
class AssetConfig:
    lifespan_years:    int
    base_failure_rate: float

ASSET_CONFIGS: dict[AssetType, AssetConfig] = {
    AssetType.OH_LINE:     AssetConfig(40, 0.05),
    AssetType.UG_CABLE:    AssetConfig(50, 0.02),
    AssetType.TRANSFORMER: AssetConfig(35, 0.04),
    AssetType.SWITCHGEAR:  AssetConfig(30, 0.03),
    AssetType.SUBSTATION:  AssetConfig(45, 0.015),
}

ASSET_COUNTS: dict[AssetType, int] = {
    AssetType.OH_LINE:     200,
    AssetType.UG_CABLE:    100,
    AssetType.TRANSFORMER: 120,
    AssetType.SWITCHGEAR:  50,
    AssetType.SUBSTATION:  30,
}

NETWORK_ZONES: list[str] = [
    "Pukekohe", "Waiuku", "Tuakau", "Pokeno", "Clarks_Beach"
]

@dataclass(slots=True)
class ScoredAsset:
    asset:          Asset
    pof_score:      float
    cof_score:      float
    risk_score:     float
    priority_tier:  PriorityTier