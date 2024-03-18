from orcaparse.regex_settings import RegexSettings


def test_regex_settings():
    reg = RegexSettings()

    # Verify that `regexes` is not None or empty
    assert reg.regexes is not None
    assert len(reg.regexes) > 0
