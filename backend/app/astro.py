"""Traditional Jyotish calculations. Sidereal Lahiri, whole-sign houses.
Swiss Ephemeris built-in Moshier calculations are used; no downloaded ephemeris required.
"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import swisseph as swe

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
NAKSHATRAS = ['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishta','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati']
LORDS = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
YEARS = [7,20,6,10,7,18,16,19,17]
PLANETS = {'Sun':swe.SUN,'Moon':swe.MOON,'Mars':swe.MARS,'Mercury':swe.MERCURY,'Jupiter':swe.JUPITER,'Venus':swe.VENUS,'Saturn':swe.SATURN,'Rahu':swe.MEAN_NODE}
YEAR_DAYS = 365.2425

def nakshatra(longitude):
    i = int((longitude % 360)/(360/27))
    return {'name': NAKSHATRAS[i], 'pada':int(((longitude%(360/27))/(360/108)))+1,'lord':LORDS[i%9]}

def location_at(lon, asc_sign):
    sign = int((lon%360)//30)
    return {'longitude':round(lon%360,4),'sign':SIGNS[sign],'sign_index':sign,'degree':round(lon%30,4),'house':((sign-asc_sign)%12)+1,'nakshatra':nakshatra(lon)}

def divisional_sign(lon, division):
    sign=int(lon//30); degree=lon%30
    if division==9:
        # Each sign spans nine navamsas. Movable start same sign; fixed starts ninth; dual starts fifth.
        start = (sign + (0 if sign%3==0 else 8 if sign%3==1 else 4))%12
        return (start+min(8,int(degree/(30/9))))%12
    if division==10:
        # Dashamsa: odd signs start from same sign; even signs start ninth from sign.
        start=(sign+(0 if sign%2==0 else 8))%12
        return (start+min(9,int(degree/3)))%12
    raise ValueError('Unsupported division')

def calculate(date, time, timezone_name, latitude, longitude):
    local=datetime.fromisoformat(f'{date}T{time}').replace(tzinfo=ZoneInfo(timezone_name))
    utc=local.astimezone(timezone.utc)
    jd=swe.julday(utc.year,utc.month,utc.day,utc.hour+utc.minute/60+utc.second/3600)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags=swe.FLG_MOSEPH|swe.FLG_SIDEREAL|swe.FLG_SPEED
    asc_tropical=swe.houses_ex(jd,latitude,longitude,b'P')[1][0]
    asc=(asc_tropical-swe.get_ayanamsa_ut(jd))%360
    asc_sign=int(asc//30)
    planets={}
    for name,body in PLANETS.items():
        vals,_=swe.calc_ut(jd,body,flags)
        planets[name]={**location_at(vals[0],asc_sign),'retrograde':vals[3]<0}
    planets['Ketu']={**location_at((planets['Rahu']['longitude']+180)%360,asc_sign),'retrograde':True}
    charts={}
    for n in (9,10):
        da=divisional_sign(asc,n)
        charts[f'D{n}']={'ascendant':SIGNS[da], 'planets':{k:{'sign':SIGNS[divisional_sign(v['longitude'],n)],'house':((divisional_sign(v['longitude'],n)-da)%12)+1} for k,v in planets.items()}}
    moon=planets['Moon']['longitude']; nak_i=int(moon/(360/27)); lord_index=nak_i%9
    elapsed=(moon%(360/27))/(360/27)
    first_start=utc-timedelta(days=YEARS[lord_index]*YEAR_DAYS*elapsed)
    dashas=[]; cursor=first_start
    for i in range(12):
        idx=(lord_index+i)%9; end=cursor+timedelta(days=YEARS[idx]*YEAR_DAYS)
        if end>=utc:
            dashas.append({'lord':LORDS[idx],'start':cursor.date().isoformat(),'end':end.date().isoformat(),'subperiods':subperiods(idx,cursor,end)})
        cursor=end
    return {'birth_utc':utc.isoformat(),'ayanamsa':'Lahiri','house_system':'Whole sign','node_type':'Mean lunar node','ephemeris':'Swiss Ephemeris / Moshier','ascendant':location_at(asc,asc_sign),'planets':planets,'divisional':charts,'dashas':dashas}

def subperiods(major_index,start,end):
    duration=(end-start).total_seconds(); cursor=start; out=[]
    for offset in range(9):
        idx=(major_index+offset)%9
        nxt=cursor+timedelta(seconds=duration*YEARS[idx]/120)
        out.append({'lord':LORDS[idx],'start':cursor.date().isoformat(),'end':nxt.date().isoformat()})
        cursor=nxt
    return out

def transit_today():
    now=datetime.now(timezone.utc)
    jd=swe.julday(now.year,now.month,now.day,now.hour+now.minute/60)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return {'date':now.date().isoformat(),'planets':{name:location_at(swe.calc_ut(jd,body,swe.FLG_MOSEPH|swe.FLG_SIDEREAL)[0][0],0) for name,body in PLANETS.items()}}
