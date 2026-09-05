"""
test_wait_for.py
------------------
Pruebas unitarias de utils/wait_for.py: no involucran red real, solo
funciones `check_fn` de prueba que simulan exito/fallo.
"""

import pytest

from utils.wait_for import DependencyNotReadyError, wait_for


def test_wait_for_retorna_de_inmediato_si_check_fn_es_true():
    calls = []

    def check():
        calls.append(1)
        return True

    wait_for(check, name="servicio-ok", max_attempts=5, initial_delay=0.01)
    assert len(calls) == 1


def test_wait_for_reintenta_hasta_exito(mocker):
    mocker.patch("utils.wait_for.time.sleep")  # no dormir de verdad en el test
    attempts = {"n": 0}

    def check():
        attempts["n"] += 1
        return attempts["n"] >= 3

    wait_for(check, name="servicio-lento", max_attempts=5, initial_delay=0.01)
    assert attempts["n"] == 3


def test_wait_for_lanza_error_tras_agotar_intentos(mocker):
    mocker.patch("utils.wait_for.time.sleep")

    def check():
        return False

    with pytest.raises(DependencyNotReadyError):
        wait_for(check, name="servicio-caido", max_attempts=3, initial_delay=0.01)


def test_wait_for_tolera_excepciones_en_check_fn(mocker):
    mocker.patch("utils.wait_for.time.sleep")
    attempts = {"n": 0}

    def check():
        attempts["n"] += 1
        if attempts["n"] < 2:
            raise ConnectionError("simulado")
        return True

    wait_for(check, name="servicio-con-error-transitorio", max_attempts=5, initial_delay=0.01)
    assert attempts["n"] == 2
