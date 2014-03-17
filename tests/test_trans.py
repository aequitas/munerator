from munerator.trans import translate, regexes
import pytest


@pytest.mark.parametrize("line,kind", [
    ['126031: client:4 health:-19 damage:20 armor:0', 'hit'],
    ['442831: client:0 health:40 damage:6 armor:0', 'hit'],
    ['Kill: 1 6 1: Ukrainian General killed yakherder by MOD_SHOTGUN', 'kill'],
    ['0:48 Item: 0 item_quad', 'quad'],
])
def test_translations(line, kind):
    assert list(translate(line, regexes))[0][0] == kind
