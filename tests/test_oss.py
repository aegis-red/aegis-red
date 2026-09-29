from aegis_red.oss import REPO_NAME, clone_url, mac_command, windows_command


def test_clone_identity_is_aegis_red_no_spaces():
    assert REPO_NAME == "aegis-red"
    assert " " not in REPO_NAME
    assert clone_url() == "https://github.com/aegis-red/aegis-red.git"
    assert "cd aegis-red" in mac_command()
    assert "cd aegis-red" in windows_command()
    assert "<this-repo-url>" not in mac_command()
