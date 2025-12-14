from waketbox import DigitGame


def test_box():
    game = DigitGame("helloworld")
    raw = "32roqworisdonasdfjqiqirqieru938345ev !@#$%^&***()_+\n\t\r\n"
    pad = game.black(raw)
    assert len(pad) <= len(raw) * 4 + game.token_length
    assert game.white(pad) == raw
