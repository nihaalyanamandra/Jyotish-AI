import os
from datetime import date
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .astro import calculate, transit_today

app=FastAPI(title='Jyotish AI API',version='0.1.0')
origins=os.getenv('CORS_ORIGINS','http://localhost:3000').split(',')
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=['GET','POST'],allow_headers=['*'])

class Birth(BaseModel):
    date: date
    time: str = Field(pattern=r'^([01]\d|2[0-3]):[0-5]\d$')
    timezone: str = 'Asia/Kolkata'
    latitude: float = Field(ge=-90,le=90)
    longitude: float = Field(ge=-180,le=180)

class ChatRequest(BaseModel):
    birth: Birth
    question: str = Field(min_length=1,max_length=3000)
    history: list[dict] = Field(default_factory=list,max_length=12)

@app.get('/health')
def health():return {'ok':True}

@app.post('/chart')
def chart(birth:Birth):
    try:return calculate(birth.date.isoformat(),birth.time,birth.timezone,birth.latitude,birth.longitude)
    except Exception as exc:raise HTTPException(status_code=422,detail=str(exc))

@app.get('/transits')
def transits():return transit_today()

@app.post('/chat')
async def chat(request:ChatRequest):
    try:chart_data=calculate(request.birth.date.isoformat(),request.birth.time,request.birth.timezone,request.birth.latitude,request.birth.longitude)
    except Exception as exc:raise HTTPException(status_code=422,detail=str(exc))
    api_key=os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {'answer':'Your chart has been calculated. '+f"Ascendant: {chart_data['ascendant']['sign']}; Moon: {chart_data['planets']['Moon']['sign']} ({chart_data['planets']['Moon']['nakshatra']['name']}). "+'Set OPENAI_API_KEY on the backend to enable conversational interpretation. Astrology is a cultural interpretive tradition, not a reliable method for predicting specific outcomes.','mode':'offline'}
    from openai import AsyncOpenAI
    client=AsyncOpenAI(api_key=api_key)
    summary={'ascendant':chart_data['ascendant'],'planets':chart_data['planets'],'dashas':chart_data['dashas'][:3],'divisional':chart_data['divisional']}
    system=('You are a knowledgeable Vedic Jyotish interpreter. Use ONLY the supplied computed chart for placements and dasha dates. '
      'Distinguish calculations from traditional interpretations. Do not fabricate sub-subperiods, yogas, marriage dates, employment outcomes or certainty. '
      'Avoid fatalistic, fear-inducing or dependency-creating claims. Do not make medical/legal/financial decisions for the user. '
      'Be direct, empathetic, and practical. If asked for a forecast, describe possibilities and uncertainty. '
      f'COMPUTED CHART: {summary}')
    messages=[{'role':'system','content':system}]
    for m in request.history[-10:]:
        if m.get('role') in ('user','assistant') and isinstance(m.get('content'),str):messages.append({'role':m['role'],'content':m['content'][:3000]})
    messages.append({'role':'user','content':request.question})
    try:
        response=await client.chat.completions.create(model=os.getenv('OPENAI_MODEL','gpt-4.1-mini'),messages=messages,temperature=0.4)
        return {'answer':response.choices[0].message.content,'mode':'ai'}
    except Exception as exc:raise HTTPException(status_code=502,detail='AI provider request failed; check backend configuration.') from exc
