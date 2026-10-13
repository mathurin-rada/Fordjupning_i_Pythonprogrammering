from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReportConfig:
    """Samlar körningens sökvägar utan att läsa eller skriva filer."""

    input_file: Path = Path("data/orders.csv")
    output_dir: Path = Path("output")
