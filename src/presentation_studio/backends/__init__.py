from __future__ import annotations

from collections.abc import Callable


def register_builtin_backends(
    register_backend: Callable[[str, Callable[..., object]], None],
    register_renderer: Callable[[str, Callable[..., object]], None],
) -> None:
    """Đăng ký adapter tích hợp khi CLI chạy, không tạo side effect lúc import."""
    from .pptx_native import build_workspace, render_workspace

    register_backend("pptx-native", build_workspace)
    register_renderer("pptx-native", render_workspace)


__all__ = ["register_builtin_backends"]
