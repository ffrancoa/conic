from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceMetadata:
    citation: str
    doi: str
    license: str
    record: str
    reference: str
    id_col: str = "Sorted ID"


PREMSTALLER = SourceMetadata(
    citation=(
        "Oberhollenzer, S., Premstaller, M., Marte, R., Tschuchnigg, F., "
        "Erharter, G.H., Marcher, T. (2021). Cone Penetration Test Dataset "
        "Premstaller Geotechnik. Data in Brief, 34, 106618."
    ),
    doi="10.1016/j.dib.2020.106618",
    license="CC BY 4.0",
    record="20805457",
    reference="Oberhollenzer et al. (2021)",
)

TAILINGS = SourceMetadata(
    citation=(
        "Arnold, C., Macedo, J. (2023). A Novel Experimental Database on the "
        "Cyclic Response of Mine Tailings. DesignSafe-CI."
    ),
    doi="10.17603/ds2-1k0a-dt17",
    license="CC BY 4.0",
    record="20807062",
    reference="Arnold & Macedo (2023)",
)

CANTERBURY = SourceMetadata(
    citation=(
        "Geyin, M., Maurer, B.W., Bradley, B.A., Green, R.A., "
        "van Ballegooy, S. (2020). CPT-Based Liquefaction Case Histories "
        "Resulting from the 2010-2016 Canterbury, New Zealand, Earthquakes: "
        "A Curated Digital Dataset. DesignSafe-CI."
    ),
    doi="10.17603/ds2-tygh-ht91",
    license="ODC-By v1.0",
    record="20839217",
    reference="Geyin et al. (2020)",
)
