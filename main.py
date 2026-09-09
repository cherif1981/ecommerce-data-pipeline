from src.ecommerce_pipeline.pipeline import cli_command


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print(
            "Usage: python main.py <csv_file>\n"
            "Example: python main.py data/samples/orders.csv"
        )
        sys.exit(1)

    cli_command(sys.argv[1])