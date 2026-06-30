import sys
from supabase import create_client

# 1. Configuration & Keys
SUPABASE_URL = "https://skwrstisakfwcmxcvpxh.supabase.co" 
SUPABASE_KEY ="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrd3JzdGlzYWtmd2NteGN2cHhoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MjgzMzI1OSwiZXhwIjoyMDk4NDA5MjU5fQ.3w6LL06XyG8qu8yh2zhtp9GtAdTNAV53r2Qz45mY2jg"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"❌ Supabase Connection Error: {e}")
    sys.exit(1)

# High-Value Tier List for Central NJ Municipalities
# High-density or strictly capped towns score higher baseline value
TOWN_WEIGHTS = {
    "PRINCETON": 40, "EDISON": 40, "HAMILTON": 38, "WOODBRIDGE": 38,
    "NEW BRUNSWICK": 35, "ASBURY PARK": 35, "RED BANK": 35, "Middletown": 32,
    "PISCATAWAY": 30, "EAST BRUNSWICK": 30, "WEST WINDSOR": 30, "FREEHOLD TWP": 30
}

def calculate_deal_metrics(license_row):
    town = license_row.get("municipality", "").upper()
    status = license_row.get("status_desc", "")
    
    # Base Score starts at 30
    score = 30
    notes = []
    
    # 1. Evaluate Township Premium (Max 40 points)
    town_bonus = TOWN_WEIGHTS.get(town, 25) # Default 25 for general local areas
    score += town_bonus
    if town_bonus >= 35:
        notes.append("High-premium commercial tier municipality.")
        
    # 2. Evaluate Status Portability (Max 30 points)
    # Pocket licenses are unlinked to real estate, making them highly portable
    if "Pocket" in status:
        score += 30
        notes.append("Pocket Status: Unlinked asset, highly portable for acquisition.")
    elif "Inactive" in status:
        score += 15
        notes.append("Inactive Status: Potentially tied to shuttered real estate.")
        
    # Cap total score at 100 max
    final_score = min(score, 100)
    
    # Fallback note if empty
    if not notes:
        notes.append("Standard local commercial asset baseline.")
        
    return final_score, " | ".join(notes)

def run_scout_analysis():
    print("🕵️‍♂️ NJ Deal Scout: Scanning raw license database records...")
    
    # Pull down all unanalyzed or raw targets from your table
    try:
        response = supabase.table("liquor_licenses").select("*").execute()
        records = response.data
    except Exception as e:
        print(f"❌ Failed to fetch table data: {e}")
        return

    if not records:
        print("ℹ️ No records found to analyze. Run sync_licenses.py first.")
        return

    print(f"🧠 Processing {len(records)} targets through Scout scoring matrix...")
    flagged_deals = 0

    for row in records:
        license_id = row["license_id"]
        
        # Run matrix calculation
        deal_score, agent_notes = calculate_deal_metrics(row)
        
        # Update the row with our newly added intelligence columns
        try:
            supabase.table("liquor_licenses").update({
                "deal_score": deal_score,
                "agent_notes": agent_notes
            }).eq("license_id", license_id).execute()
            
            if deal_score >= 70:
                print(f"🔥 HIGH VALUE DEAL [{deal_score}/100] discovered in {row['municipality']}! (ID: {license_id})")
                flagged_deals += 1
                
        except Exception as e:
            print(f"⚠️ Error updating analysis for {license_id}: {e}")

    print(f"🏁 Scout run complete. Evaluated {len(records)} assets. Flagged {flagged_deals} high-priority opportunities.")

if __name__ == "__main__":
    run_scout_analysis()