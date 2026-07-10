import os
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class PDFService:
    @classmethod
    def generate_trip_pdf(cls, trip_data: dict) -> BytesIO:
        """
        Generates a beautifully structured PDF document for the travel itinerary.
        Returns a BytesIO stream of the compiled PDF.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        
        styles = getSampleStyleSheet()
        
        # Define modern color palette matching our brand
        primary_color = colors.HexColor("#aa3bff")    # Purple accent
        secondary_color = colors.HexColor("#16171d")  # Dark theme background
        text_dark = colors.HexColor("#2e303a")        # Body text
        bg_light = colors.HexColor("#f4f3ec")         # Light code/card background
        
        # Custom Typography Styles
        title_style = ParagraphStyle(
            'CoverTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=28,
            leading=34,
            textColor=primary_color,
            alignment=0, # Left-aligned
            spaceAfter=15
        )
        
        subtitle_style = ParagraphStyle(
            'CoverSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#6b6375"),
            spaceAfter=30
        )
        
        h1_style = ParagraphStyle(
            'HeadingH1',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=secondary_color,
            spaceBefore=15,
            spaceAfter=10,
            keepWithNext=True
        )
        
        h2_style = ParagraphStyle(
            'HeadingH2',
            parent=styles['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=primary_color,
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'BodyDark',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=text_dark,
            spaceAfter=8
        )
        
        meta_label_style = ParagraphStyle(
            'MetaLabel',
            parent=body_style,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor("#08060d")
        )
        
        story = []
        
        # --- TITLE SECTION / COVER ---
        story.append(Spacer(1, 20))
        story.append(Paragraph("TripPilot AI Travel Plan", title_style))
        source = trip_data.get("source", "N/A")
        dest = trip_data.get("destination", "N/A")
        story.append(Paragraph(f"Custom Travel Itinerary: {source} to {dest}", subtitle_style))
        
        # Meta Details Box
        meta_data = [
            [Paragraph("Start Date:", meta_label_style), Paragraph(trip_data.get("start_date", "N/A"), body_style),
             Paragraph("End Date:", meta_label_style), Paragraph(trip_data.get("end_date", "N/A"), body_style)],
            [Paragraph("Total Budget:", meta_label_style), Paragraph(f"INR {trip_data.get('budget', 'N/A')}", body_style),
             Paragraph("Trip Type:", meta_label_style), Paragraph(trip_data.get("details", {}).get("trip_type", "Family Trip"), body_style)]
        ]
        
        meta_table = Table(meta_data, colWidths=[1.2*inch, 2.0*inch, 1.2*inch, 2.0*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_light),
            ('PADDING', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor("#e5e4e7")),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 25))
        
        # --- TRIP SUMMARY ---
        story.append(Paragraph("Trip Summary", h1_style))
        summary_text = trip_data.get("details", {}).get("summary", "No summary available.")
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 15))
        
        # --- TRANSPORTATION ---
        story.append(Paragraph("Transportation Recommendations", h1_style))
        
        flights = trip_data.get("details", {}).get("flights", [])
        if flights:
            story.append(Paragraph("Recommended Flights", h2_style))
            for f in flights[:2]:
                flight_info = (
                    f"<b>{f.get('airline')} ({f.get('flight_number')})</b><br/>"
                    f"Departure: {f.get('departure', {}).get('airport')} ({f.get('departure', {}).get('iata')}) "
                    f"at {f.get('departure', {}).get('scheduled')}<br/>"
                    f"Arrival: {f.get('arrival', {}).get('airport')} ({f.get('arrival', {}).get('iata')}) "
                    f"at {f.get('arrival', {}).get('scheduled')}"
                )
                story.append(Paragraph(flight_info, body_style))
                story.append(Spacer(1, 5))
        
        trains = trip_data.get("details", {}).get("trains", [])
        if trains:
            story.append(Paragraph("Recommended Trains", h2_style))
            for t in trains[:2]:
                train_info = (
                    f"<b>{t.get('train_name')} ({t.get('train_number')})</b><br/>"
                    f"Route: {t.get('from_station')} to {t.get('to_station')}<br/>"
                    f"Timing: Departure {t.get('departure')}, Arrival {t.get('arrival')} | Duration: {t.get('duration')}<br/>"
                    f"Classes: {', '.join(t.get('classes', []))} | Fares: " + 
                    ", ".join([f"{k}: Rs.{v}" for k, v in t.get('fares', {}).items()])
                )
                story.append(Paragraph(train_info, body_style))
                story.append(Spacer(1, 5))
                
        if not flights and not trains:
            story.append(Paragraph("No direct transportation listings recommended. Local cab options are recommended.", body_style))
        story.append(Spacer(1, 15))
        
        # --- ACCOMMODATION ---
        story.append(Paragraph("Hotel Options", h1_style))
        hotels = trip_data.get("details", {}).get("hotels", [])
        if hotels:
            for h in hotels:
                hotel_info = (
                    f"<b>{h.get('name')}</b> (Rating: {h.get('rating')})<br/>"
                    f"Price per night: INR {h.get('price_per_night')}<br/>"
                    f"{h.get('description')}<br/>"
                    f"Website: <font color='#aa3bff'><u>{h.get('link')}</u></font>"
                )
                story.append(Paragraph(hotel_info, body_style))
                story.append(Spacer(1, 6))
        else:
            story.append(Paragraph("No hotel recommendations available.", body_style))
        story.append(Spacer(1, 15))
        
        # --- BUDGET BREAKDOWN ---
        story.append(Paragraph("Estimated Cost Analysis", h1_style))
        budget_info = trip_data.get("details", {}).get("budget_analysis", {})
        if budget_info:
            budget_data = [
                [Paragraph("Category", meta_label_style), Paragraph("Estimated Cost (INR)", meta_label_style)],
                [Paragraph("Transportation", body_style), Paragraph(str(budget_info.get("transportation_est", 0.0)), body_style)],
                [Paragraph("Accommodation", body_style), Paragraph(str(budget_info.get("accommodation_est", 0.0)), body_style)],
                [Paragraph("Sightseeing & Activities", body_style), Paragraph(str(budget_info.get("sightseeing_est", 0.0)), body_style)],
                [Paragraph("Food & Miscellaneous", body_style), Paragraph(str(budget_info.get("food_misc_est", 0.0)), body_style)],
                [Paragraph("<b>Total Estimate</b>", meta_label_style), Paragraph(f"<b>INR {budget_info.get('total_estimated', 0.0)}</b>", meta_label_style)],
                [Paragraph("Allocated Budget Limit", body_style), Paragraph(f"INR {budget_info.get('allocated_budget', 0.0)}", body_style)],
                [Paragraph("Budget Status", body_style), Paragraph(f"<b>{budget_info.get('status', 'N/A')}</b>", body_style)]
            ]
            budget_table = Table(budget_data, colWidths=[3.2*inch, 3.2*inch])
            budget_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e5e4e7")),
                ('PADDING', (0,0), (-1,-1), 6),
                ('BACKGROUND', (0,0), (-1,0), bg_light),
            ]))
            story.append(budget_table)
            
            story.append(Spacer(1, 8))
            story.append(Paragraph("<b>Planner Recommendations:</b>", h2_style))
            for tip in budget_info.get("saving_tips", []):
                story.append(Paragraph(f"• {tip}", body_style))
        else:
            story.append(Paragraph("Budget analysis currently unavailable.", body_style))
            
        story.append(PageBreak()) # Move to next page for day-wise itinerary
        
        # --- DAY-WISE ITINERARY ---
        story.append(Paragraph("Day-by-Day Travel Itinerary", title_style))
        itinerary = trip_data.get("details", {}).get("itinerary", [])
        if itinerary:
            for day in itinerary:
                day_story = []
                day_story.append(Paragraph(f"Day {day.get('day')}: {day.get('theme')}", h1_style))
                
                activities_data = [
                    [Paragraph("<b>Time</b>", meta_label_style), 
                     Paragraph("<b>Activity Detail</b>", meta_label_style), 
                     Paragraph("<b>Location</b>", meta_label_style)]
                ]
                
                for act in day.get("activities", []):
                    desc = f"<b>{act.get('title')}</b><br/>{act.get('description')}"
                    activities_data.append([
                        Paragraph(act.get("time", ""), body_style),
                        Paragraph(desc, body_style),
                        Paragraph(act.get("location", ""), body_style)
                    ])
                    
                act_table = Table(activities_data, colWidths=[1.2*inch, 3.8*inch, 1.4*inch])
                act_table.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e5e4e7")),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('PADDING', (0,0), (-1,-1), 8),
                    ('BACKGROUND', (0,0), (-1,0), bg_light),
                ]))
                day_story.append(act_table)
                day_story.append(Spacer(1, 15))
                
                # Keep daily itinerary sections intact together on pages
                story.append(KeepTogether(day_story))
        else:
            story.append(Paragraph("No day-wise activities compiled.", body_style))
            
        # Build Document
        doc.build(story)
        buffer.seek(0)
        return buffer
