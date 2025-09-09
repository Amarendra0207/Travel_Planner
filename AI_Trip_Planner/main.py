from airportsdata import load
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agent.agentic_workflow import GraphBuilder

from fastapi.responses import JSONResponse
from utils.model_loaders import ModelLoader
import utils.model_loaders
from dotenv import load_dotenv
load_dotenv()
import os
from utils.car_rental_service import CarRentalService
from utils.airport_distance_calculator import AirportDistanceCalculator
from utils.word_document_exporter import WordDocumentExporter

app=FastAPI()

class QueryRequest(BaseModel):
    query: str = None
    question: str = None
    budget_preference: str = "budget_friendly"  # New field: cheapest, budget_friendly, luxurious
    startLocationCode: str = None  # IATA or city code for origin
    endLocationCode: str = None    # IATA or city code for destination
    startCity: str = None          # City name for origin (optional)
    endCity: str = None            # City name for destination (optional)

class WordExportRequest(BaseModel):
    content: str
    query_info: dict = None
    
@app.post("/query")
async def query_travel_agent(query:QueryRequest):
    """
    Example request body:
        {
            "query": "Plan a trip from New York to London",
            "startLocationCode": "JFK",
            "endLocationCode": "LHR"
        }
    """
    try:
        print(query)
        
        # Get budget preference from request
        budget_preference = getattr(query, 'budget_preference', 'budget_friendly')
        print(f"Budget preference: {budget_preference}")
        
        # Initialize graph with budget preference
        graph = GraphBuilder(model_provider="groq", budget_preference=budget_preference)
        react_app=graph()
        
        png_graph = react_app.get_graph().draw_mermaid_png()
        with open("my_graph.png", "wb") as f:
            f.write(png_graph)

        print(f"Graph saved as 'my_graph.png' in {os.getcwd()}")
        
        # Support both 'query' and 'question' fields
        user_query = query.query if query.query is not None else query.question
        
        # Add budget context to the query
        budget_display = {
            "cheapest": "ultra budget-friendly",
            "budget_friendly": "good value for money", 
            "luxurious": "premium luxury"
        }.get(budget_preference, "good value for money")
        
        # Add airport context to the query if provided
        if query.startLocationCode or query.endLocationCode or query.startCity or query.endCity:
            context_info = []
            if query.startLocationCode:
                context_info.append(f"Starting from airport: {query.startLocationCode}")
            if query.endLocationCode:
                context_info.append(f"Destination airport: {query.endLocationCode}")
            if query.startCity:
                context_info.append(f"Starting city: {query.startCity}")
            if query.endCity:
                context_info.append(f"Destination city: {query.endCity}")
            
            enhanced_query = f"{user_query}\n\nBudget Preference: I prefer {budget_display} travel options.\n\nAdditional Context: {', '.join(context_info)}\n\nPlease include distance information from airports to attractions in your response and tailor all recommendations to my budget preference."
        else:
            enhanced_query = f"{user_query}\n\nBudget Preference: I prefer {budget_display} travel options.\n\nPlease include distance information from airports to attractions in your response and tailor all recommendations to my budget preference."
        
        messages={"messages": [enhanced_query]}
        
        output = react_app.invoke(messages)

        # If result is dict with messages:
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content  # Last AI response
        else:
            final_output = str(output)

        # --- Car Rental Integration ---
        car_rental_section = "\n\n## Car Rental Options\n"
        try:
            car_rental_service = CarRentalService()
            airports = load('IATA')
            def city_to_iata(city_name):
                city_name = city_name.lower().strip()
                for code, data in airports.items():
                    if data.get('city', '').lower() == city_name:
                        return code
                return None

            # Use codes from request, or try to convert city names, fallback to CCU
            start_code = query.startLocationCode or (city_to_iata(query.startCity) if query.startCity else None) or "CCU"
            end_code = query.endLocationCode or (city_to_iata(query.endCity) if query.endCity else None) or "CCU"
            car_rentals = car_rental_service.search_cars(
                startLocationCode=start_code,
                endLocationCode=end_code,
                transferType="HOURLY",
                startDateTime="2025-10-10T10:00:00",
                duration="PT9H30M",
                passengers=1
              #  currency="INR"
            )
            # Handle response according to response.json format
            if isinstance(car_rentals, dict) and 'data' in car_rentals:
                for offer in car_rentals['data']:
                    vehicle = offer.get('vehicle', {})
                    provider = offer.get('serviceProvider', {})
                    partner = offer.get('partnerInfo', {}).get('serviceProvider', {})
                    quotation = offer.get('quotation', {})
                    cancellation = offer.get('cancellationRules', [{}])[0].get('ruleDescription', 'N/A')
                    desc = vehicle.get('description', 'N/A')
                    seats = vehicle.get('seats', [{}])[0].get('count', 'N/A')
                    baggages = vehicle.get('baggages', [{}])[0].get('count', 'N/A')
                    provider_name = provider.get('name', partner.get('name', 'N/A'))
                    price = quotation.get('monetaryAmount', 'N/A')
                    currency = quotation.get('currencyCode', 'N/A')
                    car_rental_section += (
                        f"- Vehicle: {desc} | Seats: {seats} | Baggage: {baggages} | Provider: {provider_name} | Price: {price} {currency}\n"
                        f"  Cancellation: {cancellation}\n"
                    )
            else:
                car_rental_section += str(car_rentals) + "\n"
        except Exception as e:
            car_rental_section += f"Car rental info unavailable: {e}\n"

        # --- Distance Information Integration ---
        distance_section = "\n\n"
        try:
            distance_calculator = AirportDistanceCalculator()
            
            # If airport codes are provided, calculate distances
            if query.startLocationCode or query.endLocationCode:
                airport_code = query.startLocationCode or query.endLocationCode
                destination_city = query.endCity or query.startCity or "the destination"
                
                distance_section += f"### Airport Distance Information\n\n"
                
                # Find major attractions in the destination city and calculate distances
                major_attractions = [
                    f"{destination_city} city center",
                    f"downtown {destination_city}",
                    f"main tourist area {destination_city}"
                ]
                
                for attraction in major_attractions:
                    distance_info = distance_calculator.get_airport_to_attraction_distance(airport_code, attraction)
                    distance_section += distance_calculator.format_distance_info(distance_info) + "\n\n"
                
                # Find nearest airports to destination
                if query.endCity:
                    nearest_airports = distance_calculator.find_nearest_airports_to_city(query.endCity)
                    if nearest_airports:
                        distance_section += f"### Nearest Airports to {query.endCity}\n\n"
                        for airport in nearest_airports[:3]:
                            distance_section += f"Airport: {airport['name']} ({airport['code']}) - {airport['distance_km']} km away\n"
                        distance_section += "\n"
                        
        except Exception as e:
            distance_section += f"Distance information unavailable: {e}\n"

        # Append distance info to the report
        final_output += distance_section

        # Append car rental info to the report
        final_output += car_rental_section

        return {"answer": final_output}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/export-word")
async def export_to_word(request: WordExportRequest):
    """
    Export travel report to Word document
    
    Example request body:
        {
            "content": "Travel report content here...",
            "query_info": {
                "startCity": "New York",
                "endCity": "London",
                "startLocationCode": "JFK",
                "endLocationCode": "LHR"
            }
        }
    """
    try:
        word_exporter = WordDocumentExporter()
        
        # Create Word document
        doc_path = word_exporter.create_travel_report_doc(
            content=request.content,
            query_info=request.query_info
        )
        
        # Get filename for response
        filename = os.path.basename(doc_path)
        
        # Return file as download
        return FileResponse(
            path=doc_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to create Word document: {str(e)}"})

@app.get("/download-sample-report")
async def download_sample_report():
    """Download a sample travel report in Word format"""
    try:
        word_exporter = WordDocumentExporter()
        
        sample_content = """
# Sample Travel Plan - New York City

## Day 1: Arrival and Manhattan Exploration
- Arrive at JFK Airport
- Check into hotel in Times Square area
- Visit Central Park
- Dinner at local restaurant

### Airport Distance Information
Distance from John F Kennedy International Airport (JFK) to Times Square: 26.45 km (approximately 31m by car)

## Day 2: Museums and Culture
- Visit Metropolitan Museum of Art
- Lunch in Upper East Side
- Broadway show in the evening

## Car Rental Options
- Vehicle: Economy Car | Seats: 4 | Provider: Hertz | Price: $89 USD
"""
        
        query_info = {
            "startCity": "New York",
            "endCity": "New York", 
            "startLocationCode": "JFK",
            "endLocationCode": "JFK"
        }
        
        doc_path = word_exporter.create_travel_report_doc(sample_content, query_info)
        filename = os.path.basename(doc_path)
        
        return FileResponse(
            path=doc_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to create sample document: {str(e)}"})
    
   
