def test_documented_server_dependency_is_installed() -> None:
    import uvicorn

    assert uvicorn.__version__
