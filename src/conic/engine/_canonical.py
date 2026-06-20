# parameters
AREA_RATIO: float = 0.80
GAMMA_WATER: float = 9.81

ROLLING: int = 1
ROLLING_LABEL: str = "*"

# cleansing
CLEAN_MODE: str = "replace"

# settings
P_REF: float = 101.33
MAX_ITER: int = 999
TOLERANCE: float = 1e-4

# columns.input
COL_DEPTH: str = "Depth (m)"
COL_QC: str = "qc (MPa)"
COL_FS: str = "fs (kPa)"
COL_U2: str = "u2 (kPa)"

COL_U0: str = "u0 (kPa)"
COL_SV_TOT: str = "σv_tot (kPa)"
COL_SV_EFF: str = "σv_eff (kPa)"

COL_VS: str = "Vs (m/s)"

# columns.output
COL_QT: str = "qt (MPa)"
COL_QN: str = "qn (MPa)"

COL_QT1: str = "Qt1 (-)"
COL_RF: str = "Rf (%)"
COL_FR: str = "Fr (%)"
COL_BQ: str = "Bq (-)"
COL_U: str = "U (-)"

COL_N: str = "n (-)"
COL_QTN: str = "Qtn (-)"
COL_IC: str = "Ic (-)"
COL_CONVG: str = "convg. (-)"

COL_CD: str = "CD (-)"
COL_IB: str = "IB (-)"
