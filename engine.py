def calculate_dumpling_finances(event: dict, config: dict) -> dict:
    att = float(event.get("estimated_attendance", 500))
    category = str(event.get("category", "General")).lower()
    
    is_niche = any(tag in category for tag in ["niche", "gf", "celiac", "vegan", "wellness", "athletic"])
    demo_pct = 0.70 if is_niche else 0.12
    capture_pct = 0.22 if is_niche else 0.09
    
    projected_patrons = round(att * demo_pct * capture_pct)
    operating_hours = float(event.get("operating_hours", 6.0))
    max_service_capacity = round(config["max_plates_per_hour"] * operating_hours)
    actual_patrons = min(projected_patrons, max_service_capacity)
    
    hot_plates = actual_patrons
    frozen_packs = round(actual_patrons * config["frozen_upsell_pct"])
    
    gross_revenue = (hot_plates * config["hot_plate_price"]) + (frozen_packs * config["frozen_pack_price"])
    
    total_dumplings = (hot_plates * 6) + (frozen_packs * 4)
    food_cogs = total_dumplings * config["ingredient_cogs"]
    prep_labor_cost = total_dumplings * config["prep_labor_cogs"]
    packaging_cost = (hot_plates * 0.75) + (frozen_packs * 0.50)
    total_cogs = food_cogs + prep_labor_cost + packaging_cost
    
    dist_miles = float(event.get("distance_from_tucson_miles", 0.0))
    transit_hours = (dist_miles / 55.0) * 2.0
    total_shift_hours = operating_hours + 1.5 + transit_hours
    staff_count = 3 if actual_patrons > 250 else 2
    on_site_labor = staff_count * total_shift_hours * config["hourly_wage"]
    
    mileage_cost = dist_miles * 2.0 * 0.35
    lodging_cost = 220.00 if dist_miles > 180 else 0.00
    
    loc_lower = str(event.get("location", "")).lower()
    if dist_miles <= 50:
        permit_fee = 0.00
    elif "maricopa" in loc_lower or "phoenix" in loc_lower or "scottsdale" in loc_lower:
        permit_fee = 200.00
    elif "utah" in loc_lower or dist_miles > 400:
        permit_fee = 150.00
    else:
        permit_fee = 100.00
        
    booth_fee = float(event.get("vendor_fee_usd", 150.00))
    utility_fee = 40.00 if not event.get("power_available", True) else 0.00
    
    total_expenses = total_cogs + on_site_labor + mileage_cost + lodging_cost + permit_fee + booth_fee + utility_fee
    net_profit = gross_revenue - total_expenses
    roi = (net_profit / total_expenses) if total_expenses > 0 else 0.0
    
    if net_profit >= 1100.0 and roi >= 0.75:
        tier = "Tier 1: Green Light"
    elif net_profit >= 450.0 and dist_miles <= 140:
        tier = "Tier 2: Tactical Fill-In"
    else:
        tier = "Tier 3: Pass / Archive"
        
    return {
        "gross_revenue": round(gross_revenue, 2),
        "total_expenses": round(total_expenses, 2),
        "net_profit": round(net_profit, 2),
        "roi_text": f"{round(roi * 100, 1)}%",
        "decision_tier": tier,
        "prep_dumplings": int(total_dumplings),
        "projected_customers": int(actual_patrons)
    }
