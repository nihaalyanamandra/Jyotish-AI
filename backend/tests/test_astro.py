from app.astro import calculate,divisional_sign

def test_chart():
    c=calculate('1998-06-10','07:56','Asia/Kolkata',21.1458,79.0882)
    assert c['ascendant']['sign'] in ['Gemini','Cancer']
    assert len(c['planets'])==9
    assert len(c['divisional']['D9']['planets'])==9
    assert len(c['dashas'])>0
    assert all(len(d['subperiods'])==9 for d in c['dashas'])

def test_divisional():
    for n in (9,10):
        for degree in range(360):assert 0<=divisional_sign(degree,n)<12
