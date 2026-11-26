from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from analysis import issues
import pandas as pd

def weekly_pdf(df):
    buf=BytesIO(); styles=getSampleStyleSheet()
    if df.empty:
        story=[Paragraph('Weekly Feedback Intelligence Report',styles['Title']),Paragraph('No reviews match the selected filters.',styles['Normal'])]
        SimpleDocTemplate(buf).build(story); return buf.getvalue()
    end=df.date.max().normalize(); start=end-pd.Timedelta(days=6)
    week=df[df.date.ge(start)]
    counts=week.sentiment.value_counts()
    avg_rating=pd.to_numeric(week.rating,errors='coerce').mean() if 'rating' in week else float('nan')
    rating_text=f'{avg_rating:.2f}/5' if pd.notna(avg_rating) else 'Not provided'
    story=[Paragraph('Signal Weekly Feedback Report',styles['Title']),Paragraph(f'{start.date()} to {end.date()} | {len(week)} reviews | Average rating: {rating_text}',styles['Normal']),Spacer(1,15)]
    d=Drawing(440,180); chart=VerticalBarChart(); chart.x=45; chart.y=30; chart.width=350; chart.height=125; chart.data=[[int(counts.get(x,0)) for x in ['Positive','Neutral','Negative']]]; chart.categoryAxis.categoryNames=['Positive','Neutral','Negative']; chart.valueAxis.valueMin=0; chart.valueAxis.valueMax=max(1,int(counts.max()) if not counts.empty else 0); chart.bars[0].fillColor=colors.HexColor('#2563eb'); d.add(chart); story.append(d)
    story.append(Paragraph('Sentiment counts: '+', '.join(f'{name}: {int(counts.get(name,0))}' for name in ['Positive','Neutral','Negative']),styles['Normal']))
    story.append(Paragraph('Top recurring negative issues',styles['Heading2']))
    rows=[['Issue','Frequency','Priority']]+issues(week).values.tolist()
    if len(rows)==1: rows.append(['No matched issues',0,0])
    t=Table(rows); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dbeafe')),('GRID',(0,0),(-1,-1),.4,colors.grey)])); story.append(t)
    story.append(Paragraph('Priority is the sum of negative sentiment intensity. Review the underlying comments before taking action.',styles['Normal']))
    SimpleDocTemplate(buf).build(story); return buf.getvalue()
import pandas as pd
