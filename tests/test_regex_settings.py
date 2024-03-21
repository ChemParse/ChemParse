from orcaparse.regex_settings import RegexSettings, DEFAULT_REGEX_FILE


def test_regex_settings():
    rs = RegexSettings(settings_file=DEFAULT_REGEX_FILE)

    # Verify that `regexes` is not None or empty
    assert rs.get_ordered_items() is not None
    assert len(rs) > 0
