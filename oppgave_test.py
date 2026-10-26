"""Automatisk retting av 1T-03-vekstfart-og-derivasjon.

Hver sjekk i SJEKKER er én deltest, og poengene fordeles likt på dem.
De samme sjekkene ligger i "Test løsningen din"-cellen nederst i notebooken.
"""
import pytest

from notebook_loader import last_notebook

def naer(a, b, rel=1e-3):
    """Sant hvis tallet a er innenfor rel (relativt) av b."""
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if b == 0:
        return abs(a) < 1e-9
    return abs(a - b) <= rel * abs(b)


def S(tekst):
    """Gjør tekst om til et sympy-uttrykk, f.eks. S("x**2 - 1")."""
    import sympy
    return sympy.sympify(tekst, locals={n: sympy.Symbol(n) for n in ("N", "O", "Q", "S")})


def lik(a, b):
    """Sant hvis a og b er matematisk like.

    Lister og mengder sammenlignes uten hensyn til rekkefølge, tupler (koordinater) i rekkefølge.
    """
    import sympy
    if a is None:
        return False
    if isinstance(b, tuple):
        if not isinstance(a, (tuple, list, sympy.Tuple)) or len(a) != len(b):
            return False
        return all(lik(x, y) for x, y in zip(a, b))
    if isinstance(b, (list, set)):
        if isinstance(a, sympy.FiniteSet):
            a = list(a)
        if not isinstance(a, (list, tuple, set)) or len(a) != len(b):
            return False
        rest = list(a)
        for y in b:
            for i, x in enumerate(rest):
                if lik(x, y):
                    del rest[i]
                    break
            else:
                return False
        return True
    if isinstance(b, dict):
        if not isinstance(a, dict) or len(a) != len(b):
            return False
        a = {str(k): v for k, v in a.items()}
        return all(str(k) in a and lik(a[str(k)], v) for k, v in b.items())
    try:
        a, b = sympy.sympify(a), sympy.sympify(b)
    except (sympy.SympifyError, TypeError):
        return False
    vanlige = lambda u: u.subs({s: sympy.Symbol(s.name) for s in u.free_symbols})
    a, b = vanlige(a), vanlige(b)
    if isinstance(a, sympy.Set) or isinstance(b, sympy.Set):
        return a == b
    if getattr(b, "is_Relational", False):
        return a == b
    try:
        return sympy.simplify(a - b) == 0
    except TypeError:
        return a == b

oppgave = last_notebook("oppgave")

SJEKKER = [
    ('1_kubisk', 'gjennomsnittlig_vekstfart(x³, 1, 3) skal gi 13', 'naer(gjennomsnittlig_vekstfart(lambda x: x**3, 1, 3), 13)'),
    ('1_synkende', 'gjennomsnittlig_vekstfart(-2x + 1, 0, 5) skal gi -2', 'naer(gjennomsnittlig_vekstfart(lambda x: -2*x + 1, 0, 5), -2)'),
    ('2_kvadrat', 'momentan_vekstfart(x², 3) skal gi omtrent 6', 'naer(momentan_vekstfart(lambda x: x**2, 3), 6, rel=1e-4)'),
    ('2_kubisk', 'momentan_vekstfart(x³ - 2x, -1) skal gi omtrent 1', 'naer(momentan_vekstfart(lambda x: x**3 - 2*x, -1), 1, rel=1e-4)'),
    ('3', 'derivert_3 skal være den deriverte av 2x³ - 5x² + 4x - 7', "lik(derivert_3, S('6*x**2 - 10*x + 4'))"),
    ('4a', "stigning_kl9 skal være T'(3) = 1.2 °C per time", 'naer(stigning_kl9, 1.2)'),
    ('4b', 'varmest_t skal være 6 (klokka 12)', 'naer(varmest_t, 6)'),
    ('5_eksempel', 'deriver_polynom([2, -5, 4, -7]) skal gi [6, -10, 4]', 'list(deriver_polynom([2, -5, 4, -7])) == [6, -10, 4]'),
    ('5_konstant', 'deriver_polynom([5]) skal gi [] (en konstant har derivert 0)', 'list(deriver_polynom([5])) in ([], [0]) and list(deriver_polynom([1, 0])) == [1]'),
    ('5_hoy_grad', 'deriver_polynom([1, 0, 0, 0, 0]) skal gi [4, 0, 0, 0]', 'list(deriver_polynom([1, 0, 0, 0, 0])) == [4, 0, 0, 0]'),
]


@pytest.mark.parametrize(
    "beskrivelse,uttrykk", [s[1:] for s in SJEKKER], ids=[s[0] for s in SJEKKER]
)
def test_sjekk(beskrivelse, uttrykk):
    navnerom = {**vars(oppgave), "naer": naer, "lik": lik, "S": S}
    assert eval(uttrykk, navnerom), beskrivelse
