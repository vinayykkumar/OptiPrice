import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults

# === 🛠️ Web Search Tool ===
@tool
def search_web_tool(query: str):
    """Searches the web for travel information."""
    search_tool = DuckDuckGoSearchResults(num_results=10, verbose=True)
    return search_tool.run(query)

# === 🤖 LLM Connection (Ollama) ===
llm = LLM(model="ollama/llama3.2", base_url="http://localhost:11434")

# === 📌 Streamlit App UI ===
st.set_page_config(page_title="CrewAI Travel Planner", layout="wide")
st.title("🌍 AI-Powered Travel Planner")

# === ✍️ User Input Form ===
with st.form(key="travel_form"):
    from_city = st.text_input("🏙️ Departure City", "New York")
    destination_city = st.text_input("✈️ Destination City", "Paris")
    date_from = st.text_input("📅 Departure Date", "1st April 2025")
    date_to = st.text_input("📅 Return Date", "10th April 2025")
    interests = st.text_input("🎭 Interests (food, sightseeing, adventure)", "food, sightseeing")

    submit_button = st.form_submit_button(label="🛫 Generate Travel Plan")

# === 🔥 If Button Clicked, Process Request ===
if submit_button:
    st.write("⏳ Generating your AI-powered travel plan...")

    # === 🎭 Define Agents ===
    location_expert = Agent(
        role="Travel Location Expert",
        goal="Gather information about the city, accommodations, weather, travel advisories.",
        backstory="A seasoned travel researcher providing insights on where to stay, what to expect, and travel tips.",
        tools=[search_web_tool],
        verbose=True,
        max_iter=5,
        llm=llm,
        allow_delegation=False,
    )

    guide_expert = Agent(
        role="Local Guide Expert",
        goal="Provides recommendations for sightseeing, food, and experiences.",
        backstory="A passionate local guide with knowledge of the best spots in town.",
        tools=[search_web_tool],
        verbose=True,
        max_iter=5,
        llm=llm,
        allow_delegation=False,
    )

    planner_expert = Agent(
        role="Travel Planner Expert",
        goal="Creates a complete travel itinerary based on location and guide inputs.",
        backstory="A meticulous travel planner who ensures a seamless experience.",
        tools=[search_web_tool],
        verbose=True,
        max_iter=5,
        llm=llm,
        allow_delegation=False,
    )

    # === 📝 Define Tasks ===
    location_task = Task(
        description=f"""
        Gather **detailed travel insights** for {destination_city}.
        - Departure: {from_city}
        - Destination: {destination_city}
        - Dates: {date_from} to {date_to}

        **Must Include:**
        - Best hotels, hostels, and Airbnb recommendations with pricing
        - Daily cost breakdown: accommodation, food, transport, entertainment
        - Visa and travel restrictions
        - Weather forecast and seasonal travel tips
        - Hidden costs or common tourist scams
        """,
        expected_output="A detailed markdown report with accommodation, expenses, weather, and travel tips.",
        agent=location_expert,
        output_file="city_report.md",
    )

    guide_task = Task(
        description=f"""
        Generate a **detailed travel guide** for {destination_city} based on these interests: {interests}.
        - Dates: {date_from} to {date_to}

        **Include:**
        - **Top attractions and must-visit places**
        - **Local cuisine recommendations**
        - **Entertainment options: nightlife, shopping, cultural festivals**
        - **Hidden gems and city navigation tips**
        """,
        expected_output="A markdown guide covering attractions, food, hidden gems, and travel tips.",
        agent=guide_expert,
        output_file="guide_report.md",
    )

    planner_task = Task(
        description=f"""
        Create a **detailed travel itinerary** for {destination_city}.
        - Interests: {interests}
        - Travel Dates: {date_from} to {date_to}

        **Must Cover:**
        - **Introduction to {destination_city}** (culture, history, why visit?)
        - **Estimated budget breakdown** (daily expenses, total trip cost)
        - **Full daily itinerary** (morning, afternoon, evening plans)
        - **Local transport options & travel routes**
        - **Packing tips based on weather and cultural norms**
        """,
        expected_output="A structured 1-2 page markdown itinerary with costs, itinerary, and travel tips.",
        context=[location_task, guide_task],
        agent=planner_expert,
        output_file="travel_plan.md",
    )

    # === 🏆 Setup CrewAI Execution ===
    crew = Crew(
        agents=[location_expert, guide_expert, planner_expert],
        tasks=[location_task, guide_task, planner_task],
        process=Process.sequential,
        full_output=True,
        share_crew=False,
        verbose=True
    )

    # === 🚀 Run CrewAI & Generate Reports ===
    result = crew.kickoff()

    st.success("✅ Travel reports generated successfully!")

    # === 📜 Display Results ===
    with open("travel_plan.md", "r", encoding="utf-8") as file:
        travel_plan_content = file.read()

    st.subheader("📜 Travel Itinerary")
    st.markdown(travel_plan_content)

    # === 📥 Download Travel Plan ===
    st.download_button(
        label="📥 Download Travel Plan",
        data=travel_plan_content,
        file_name="travel_plan.md",
        mime="text/markdown"
    )
