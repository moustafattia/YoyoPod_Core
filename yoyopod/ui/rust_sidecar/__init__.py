"""Compatibility imports for the renamed Rust UI host bridge."""

from yoyopod.ui.rust_host import RustUiFacade, RustUiRuntimeSnapshot, UiEnvelope, UiProtocolError
from yoyopod.ui.rust_host.facade import RustUiFacade as RustUiSidecarCoordinator
from yoyopod.ui.rust_host.supervisor import RustUiHostSupervisor as RustUiSidecarSupervisor

__all__ = [
    "RustUiFacade",
    "RustUiRuntimeSnapshot",
    "RustUiSidecarCoordinator",
    "RustUiSidecarSupervisor",
    "UiEnvelope",
    "UiProtocolError",
]
