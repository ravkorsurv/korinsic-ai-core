"""
Bayesian models package for market abuse detection.

This package contains Bayesian network models organized by abuse type:
- insider_dealing/: Insider dealing detection models
- spoofing/: Market manipulation detection models
- latent_intent/: Advanced latent intent models
- shared/: Shared Bayesian components and utilities
"""

try:
	from .insider_dealing import InsiderDealingModel  # type: ignore
except Exception:
	InsiderDealingModel = None  # type: ignore

try:
	from .latent_intent import LatentIntentModel  # type: ignore
except Exception:
	LatentIntentModel = None  # type: ignore

try:
	from .registry import BayesianModelRegistry  # type: ignore
except Exception:
	BayesianModelRegistry = None  # type: ignore

try:
	from .shared import BayesianNodeLibrary, ModelBuilder  # type: ignore
except Exception:
	BayesianNodeLibrary = None  # type: ignore
	ModelBuilder = None  # type: ignore

try:
	from .spoofing import SpoofingModel  # type: ignore
except Exception:
	SpoofingModel = None  # type: ignore

__all__ = [
	"BayesianModelRegistry",
	"InsiderDealingModel",
	"SpoofingModel",
	"LatentIntentModel",
	"BayesianNodeLibrary",
	"ModelBuilder",
]
