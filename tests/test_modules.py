import pytest
import importlib

modules = ['changer', 'context', 'ledbar', 'listen', 'old',
           'periodic', 'rcon', 'restapi', 'store', 'trans', 'wrap']


@pytest.mark.parametrize('module_name', modules)
def test_module_entrypoints(module_name):
    """
    Simple test to check if module exists
    """
    module = importlib.import_module('munerator.%s' % module_name)
    assert module.main
