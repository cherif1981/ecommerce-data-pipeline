"""CSV data extraction module."""

import pandas as pd
from pathlib import Path

from ..exceptions import ExtractionError
from ..logging_config import get_logger

logger = get_logger(__name__)


class CSVExtractor:
    """Extract data from CSV files."""

    def __init__(self, file_path):
        self.file_path = Path(file_path)

    def extract(self):
        """
        Extract data from CSV file.
        
        Returns:
            pd.DataFrame: Extracted data.
            
        Raises:
            ExtractionError: If file reading fails.
        """
        if not self.file_path.exists():
            raise ExtractionError(f"File not found: {self.file_path}")
        
        try:
            logger.info(f"Extracting data from {self.file_path}")
            df = pd.read_csv(self.file_path)
            logger.info(f"Extracted {len(df)} rows")
            return df
        except Exception as e:
            raise ExtractionError(f"Failed to extract CSV: {e}") from e