"""Domain exceptions exposed by backend services."""


class EcoSphereError(Exception):
    """Base class for EcoSphere domain errors."""


class EnergyPlusNotFound(EcoSphereError):
    """Raised when EnergyPlus cannot be located."""


class WeatherFileMissing(EcoSphereError):
    """Raised when the configured weather file is absent."""


class BuildingFileMissing(EcoSphereError):
    """Raised when the configured building model is absent."""


class SimulationError(EcoSphereError):
    """Raised when simulation work cannot complete."""


class OllamaError(EcoSphereError):
    """Raised when Ollama cannot process a request."""


class OptimizationError(EcoSphereError):
    """Raised when an optimization workflow cannot complete."""


class IDFModificationError(EcoSphereError):
    """Raised when an IDF modification cannot be applied safely."""

