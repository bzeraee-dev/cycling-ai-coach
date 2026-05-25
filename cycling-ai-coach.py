#!/usr/bin/env python
# coding: utf-8

import os
import requests
import pandas as pd
import anthropic
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

os.environ["GMAIL_ADDRESS"] = "your_gmail@gmail.com"
os.environ["GMAIL_APP_PASSWORD"] = "your_app_password"
os.environ["STRAVA_CLIENT_ID"] = "your_client_id"
os.environ["STRAVA_CLIENT_SECRET"] = "your_client_secret"
os.environ["STRAVA_REFRESH_TOKEN"] = "your_refresh_token"
os.environ["ANTHROPIC_API_KEY"] = "your_anthropic_key"

def run_monthly_coaching_report():
    print("🚴 Starting monthly cycling coaching report...")

    print("📡 Connecting to Strava...")
    token_response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": os.environ.get("STRAVA_CLIENT_ID"),
            "client_secret": os.environ.get("STRAVA_CLIENT_SECRET"),
            "grant_type": "refresh_token",
            "refresh_token": os.environ.get("STRAVA_REFRESH_TOKEN")
        }
    )
    
    access_token = token_response.json()["access_token"]

    print("📥 Pulling your rides...")
    response = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"per_page": 50, "page": 1}
    )
    activities = response.json()
    rides = []
    for a in activities:
        if a["type"] not in ["Ride", "VirtualRide"]:
            continue
        rides.append({
            "date": a["start_date"][:10],
            "type": a["type"],
            "distance_km": round(a["distance"] / 1000, 2),
            "duration_min": round(a["moving_time"] / 60, 1),
            "elevation_m": a["total_elevation_gain"],
            "avg_speed_kmh": round(a["average_speed"] * 3.6, 2),
            "avg_heartrate": a.get("average_heartrate", None),
            "suffer_score": a.get("suffer_score", None),
        })

    df = pd.DataFrame(rides)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date", ascending=False).reset_index(drop=True)

    print("📊 Calculating metrics...")
    today = pd.Timestamp.now()
    last_30 = df[df["date"] >= today - pd.Timedelta(days=30)]
    prev_30 = df[(df["date"] >= today - pd.Timedelta(days=60)) & (df["date"] < today - pd.Timedelta(days=30))]

    distance_trend = round(last_30["distance_km"].sum() - prev_30["distance_km"].sum(), 1)
    speed_trend = round(last_30["avg_speed_kmh"].mean() - prev_30["avg_speed_kmh"].mean(), 2)

    summary = f"""
CYCLING PERFORMANCE SUMMARY — {datetime.now().strftime('%B %d, %Y')}
============================
Total rides analyzed: {len(df)}
Total distance: {df['distance_km'].sum():.1f} km
Total elevation: {df['elevation_m'].sum():.0f} m

LAST 30 DAYS
- Rides per week: {round(len(last_30) / 4, 1)}
- Total distance: {last_30['distance_km'].sum():.1f} km
- Avg speed: {round(last_30['avg_speed_kmh'].mean(), 2)} km/h
- Distance trend vs previous 30 days: {'+' if distance_trend > 0 else ''}{distance_trend} km
- Speed trend vs previous 30 days: {'+' if speed_trend > 0 else ''}{speed_trend} km/h

PERSONAL BESTS
- Fastest avg speed: {df['avg_speed_kmh'].max()} km/h
- Longest ride: {df['distance_km'].max()} km
- Most elevation in one ride: {df['elevation_m'].max():.0f} m
"""

    print("🧠 Getting AI coaching insights...")
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""You are an expert cycling coach. Analyze this performance data and provide personalized, actionable coaching insights. Be specific, encouraging, and practical.

{summary}

Additional context:
- Rider is based in Montreal, Quebec
- Mix of indoor (VirtualRide) and outdoor riding
- Completed an epic challenge: 34 laps of Camilien Houde mountain

Please provide:
1. Overall fitness assessment
2. Key strengths you observe
3. Areas to improve
4. Specific training recommendations for the next 4 weeks
5. A motivational closing remark
"""
        }]
    )
    coaching_text = message.content[0].text

    print("📧 Sending coaching report...")
    sender = os.environ.get("GMAIL_ADDRESS")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = "your_personal_email@gmail.com"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚴 Monthly Cycling Coaching Report — {datetime.now().strftime('%B %d, %Y')}"
    msg["From"] = sender
    msg["To"] = recipient

    html = f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
        <h1 style="color: #FC4C02;">🚴 Monthly Cycling Coaching Report</h1>
        <p style="color: #888;">{datetime.now().strftime('%B %d, %Y')}</p>
        <h2 style="color: #333;">📊 Your Stats</h2>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 8px;">{summary}</pre>
        <h2 style="color: #333;">🧠 Your AI Coaching Insights</h2>
        <div style="background: #fff8f0; padding: 15px; border-left: 4px solid #FC4C02; border-radius: 4px;">
            {coaching_text.replace(chr(10), '<br>')}
        </div>
        <br>
        <p style="color: #aaa; font-size: 12px;">Powered by Cycling AI Coach | Built with Strava + Claude API</p>
    </body></html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print("✅ Monthly coaching report sent successfully!")

run_monthly_coaching_report()