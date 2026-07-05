import tomllib
from pathlib import Path

_DEFAULTS_PATH = Path(__file__).parent / "defaults.toml"

with _DEFAULTS_PATH.open("rb") as _file:
    _DEFAULTS = tomllib.load(_file)

_PARAMETERS = _DEFAULTS["parameters"]
_CLEANSING = _DEFAULTS["cleansing"]
_SETTINGS = _DEFAULTS["settings"]
_INPUT = _DEFAULTS["columns"]["input"]
_OUTPUT = _DEFAULTS["columns"]["output"]
_BI14 = _DEFAULTS["columns"]["correlation"]["bi14"]
_R21 = _DEFAULTS["columns"]["correlation"]["r21"]
_OS02 = _DEFAULTS["columns"]["correlation"]["os02"]
_RW98 = _DEFAULTS["columns"]["correlation"]["rw98"]
_Y14 = _DEFAULTS["columns"]["correlation"]["y14"]

# parameters
AREA_RATIO: float = _PARAMETERS["area_ratio"]
GAMMA_WATER: float = _PARAMETERS["gamma_water"]

ROLLING: int = _PARAMETERS["rolling"]
ROLLING_LABEL: str = _PARAMETERS["rolling_label"]

# cleansing
CLEAN_MODE: str = _CLEANSING["clean_mode"]
MAX_SLEEVE_OFFSET: int = _CLEANSING["max_sleeve_offset"]

# settings
P_REF: float = _SETTINGS["p_ref"]
MAX_ITER: int = _SETTINGS["max_iter"]
TOLERANCE: float = _SETTINGS["tolerance"]

# columns.input
COL_DEPTH: str = _INPUT["depth"]
COL_QC: str = _INPUT["qc"]
COL_FS: str = _INPUT["fs"]
COL_U2: str = _INPUT["u2"]

COL_U0: str = _INPUT["u0"]
COL_SV_TOT: str = _INPUT["sv_tot"]
COL_SV_EFF: str = _INPUT["sv_eff"]

COL_VS: str = "Vs (m/s)"

# columns.output
COL_QT: str = _OUTPUT["qt"]
COL_QN: str = _OUTPUT["qn"]

COL_QT1: str = _OUTPUT["qt1"]
COL_RF: str = _OUTPUT["rf"]
COL_FR: str = _OUTPUT["fr"]
COL_BQ: str = _OUTPUT["bq"]
COL_U: str = _OUTPUT["u"]

COL_N: str = _OUTPUT["n"]
COL_QTN: str = _OUTPUT["qtn"]
COL_IC: str = _OUTPUT["ic"]
COL_CONVG: str = _OUTPUT["convg"]

COL_CD: str = _OUTPUT["cd"]
COL_IB: str = _OUTPUT["ib"]

# columns.correlation.bi14
COL_FC_BI14: str = _BI14["fc"]
COL_M_BI14: str = _BI14["m"]
COL_QC1N_BI14: str = _BI14["qc1n"]
COL_QC1NCS_BI14: str = _BI14["qc1ncs"]
COL_CONVG_BI14: str = _BI14["convg"]

# columns.correlation.r21
COL_KC_R21: str = _R21["kc"]
COL_QTNCS_R21: str = _R21["qtncs"]
COL_SU_LIQ_RATIO_R21: str = _R21["su_liq_ratio"]

# columns.correlation.os02
COL_QC1_OS02: str = _OS02["qc1"]
COL_SU_LIQ_RATIO_OS02: str = _OS02["su_liq_ratio"]

# columns.correlation.rw98
COL_FC_RW98: str = _RW98["fc"]

# columns.correlation.y14
COL_FC_Y14: str = _Y14["fc"]
