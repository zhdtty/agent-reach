from rustchain.cli import main
import sys


def test_cli_help(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["rustchain"])
    try:
        main()
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "usage" in out.lower() or "rustchain" in out.lower()
