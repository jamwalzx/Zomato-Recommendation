"""Phase 0 scaffold tests."""

import importlib


def test_import_src_package() -> None:
    import src

    assert src.__version__ == "0.1.0"


def test_import_subpackages() -> None:
    for module_name in (
        "src.models",
        "src.data",
        "src.services",
        "src.llm",
        "src.ui",
        "src.config",
        "src.main",
    ):
        module = importlib.import_module(module_name)
        assert module is not None


def test_main_returns_zero() -> None:
    from src.main import main

    assert main([]) == 0
