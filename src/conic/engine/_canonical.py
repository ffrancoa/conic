# parameters
AREA_RATIO: float = 0.80
GAMMA_WATER: float = 9.81

ROLLING: int = 1
ROLLING_LABEL: str = "*"

# cleansing
CLEAN_MODE: str = "replace"
MAX_SLEEVE_OFFSET: int = 0

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

# columns.correlation.bi14
COL_FC_BI14: str = "FC (%) [BI14]"
COL_M_BI14: str = "m (-) [BI14]"
COL_QC1N_BI14: str = "qc1n (-) [BI14]"
COL_QC1NCS_BI14: str = "qc1ncs (-) [BI14]"
COL_CONVG_BI14: str = "convg. (-) [BI14]"

# columns.correlation.r21
COL_KC_R21: str = "Kc (-) [R21]"
COL_QTNCS_R21: str = "Qtn,cs (-) [R21]"
COL_SU_LIQ_RATIO_R21: str = "Su_liq (-) [R21]"

# columns.correlation.os02
COL_QC1_OS02: str = "qc1 (MPa) [OS02]"
COL_SU_LIQ_RATIO_OS02: str = "Su_liq (-) [OS02]"

# columns.inverse_filter
COL_QT_INV: str = "qt_inv (MPa)"
COL_FS_INV: str = "fs_inv (kPa)"
COL_CONVG_INV: str = "convg. (-) [BD18]"

# inverse_filter
DC: float = 35.7
DZ: float = 20.0
Z50_REF: float = 4.2
MZ: float = 3.0
M50: float = 0.5
MQ: float = 2.0
MT: float = 0.1
STALL_TOLERANCE: float = 1e-6
