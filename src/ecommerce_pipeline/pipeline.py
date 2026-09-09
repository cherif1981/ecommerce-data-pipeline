"""Main ETL pipeline orchestration."""

from pathlib import Path
import sys

from .extraction.csv import CSVExtractor
from .validation.orders import OrderValidator
from .transformation.orders import OrderTransformer
from .loading.postgres import DatabaseLoader
from .logging_config import get_logger, setup_logging
from .config import get_config

logger = get_logger(__name__)


class ETLPipeline:
    """Orchestrate the ETL pipeline."""

    def __init__(self, source_file):
        self.source_file = Path(source_file)
        self.extractor = CSVExtractor(self.source_file)
        self.loader = DatabaseLoader()
        
    def run(self):
        """
        Run the full ETL pipeline.
        """
        logger.info(f"Starting ETL pipeline for {self.source_file}")
        
        try:
            # Extract
            raw_data = self.extractor.extract()
            
            # Validate
            validator = OrderValidator(raw_data)
            validated_data = validator.validate()
            
            # Transform
            transformer = OrderTransformer(validated_data)
            transformed_data = transformer.transform()
            
            # Load
            self.loader.load(transformed_data)
            
            logger.info("ETL pipeline completed successfully")
            print("\n" + "="*60)
            print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"📊 Data loaded into: {get_config().database.connection_string}")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            print(f"\n❌ Pipeline failed: {e}")
            raise


def cli_command(source_file):
    """
    CLI command function to run the pipeline.
    
    Args:
        source_file: Path to the CSV file
    """
    pipeline = ETLPipeline(source_file)
    pipeline.run()


def main():
    """CLI entry point."""
    import click
    
    setup_logging()
    
    @click.command()
    @click.argument("source_file", type=click.Path(exists=True))
    def cli(source_file):
        """Run the ETL pipeline from a CSV file."""
        cli_command(source_file)
    
    if len(sys.argv) > 1:
        cli()
    else:
        print("Usage: python -m src.ecommerce_pipeline.pipeline <csv_file>")
        print("Example: python -m src.ecommerce_pipeline.pipeline data/samples/orders.csv")
        sys.exit(0)


if __name__ == "__main__":
    main()