"""Custom exceptions for the ETL pipeline."""

class PipelineError(Exception):
    """Base exception for all pipeline errors."""
    pass


class ExtractionError(PipelineError):
    """Raised when data extraction fails."""
    pass


class ValidationError(PipelineError):
    """Raised when data validation fails."""
    pass


class TransformationError(PipelineError):
    """Raised when data transformation fails."""
    pass


class LoadingError(PipelineError):
    """Raised when data loading fails."""
    pass


class ConfigurationError(PipelineError):
    """Raised when configuration is invalid."""
    pass