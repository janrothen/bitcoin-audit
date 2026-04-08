import importlib


def test_project_root_uses_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv("BITCOIN_AUDIT_HOME", str(tmp_path))
    import audit.config as config_module

    importlib.reload(config_module)
    assert config_module.project_root() == tmp_path


def test_project_root_falls_back_to_file_relative(monkeypatch):
    monkeypatch.delenv("BITCOIN_AUDIT_HOME", raising=False)
    import audit.config as config_module

    importlib.reload(config_module)
    # In an editable install __file__ is src/audit/config.py, so three levels
    # up is the project root (contains pyproject.toml).
    assert (config_module.project_root() / "pyproject.toml").exists()
