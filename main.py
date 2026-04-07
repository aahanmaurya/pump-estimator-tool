import streamlit as st

st.set_page_config(page_title="Advanced Pump Skid Estimator", layout="wide")

st.title("⚙️ Advanced Pump Skid Estimator (Pro Version)")
st.markdown("Detailed estimation model with extended hydraulic, electrical, and mechanical parameters.")

# --- BACKEND DATA & MATRICES ---
moc_multipliers = {'CI': 1.0, 'Bronze': 1.5, 'SS316': 2.5, 'Duplex': 4.0, 'Super_Duplex': 5.5}
seal_plan_costs = {'Plan 11': 2000, 'Plan 52': 55000, 'Plan 53A': 75000}
bellows_cost = {'2_inch': 3500, '3_inch': 5000, '4_inch': 7500, '6_inch': 12000}

# Motor Pricing Multipliers (Market Constants)
base_motor_rate_per_kw = 3200 
motor_type_mult = {'Standard (Safe Area)': 1.0, 'Flameproof (FLP)': 1.6}
motor_rpm_mult = {'1500 RPM': 1.0, '3000 RPM': 0.95} 
motor_protection_mult = {'IP55': 1.0, 'IP66': 1.15}

vfd_rate_per_kw = 4500     
base_plate_per_kg = 95     

# --- UI INPUTS ---
st.subheader("1. Hydraulic & Mechanical Data")
col1, col2, col3, col4 = st.columns(4)
with col1:
    flow = st.number_input("Flowrate (m³/hr)", min_value=1.0, value=50.0)
with col2:
    head = st.number_input("Head (meters)", min_value=1.0, value=120.0)
with col3:
    stages = st.number_input("No. of Stages", min_value=1, value=1)
with col4:
    impeller_dia = st.number_input("Impeller Diameter (mm)", min_value=100.0, value=250.0)

moc = st.selectbox("Material of Construction (MOC)", options=list(moc_multipliers.keys()), index=2)

st.divider()

st.subheader("2. Drive & Electrical Specifications")
col1, col2, col3 = st.columns(3)
with col1:
    shaft_power = st.number_input("Pump Shaft Power (kW)", min_value=0.5, value=30.0)
    # Automatically add 15% safety margin to get motor size
    motor_kw = shaft_power * 1.15
    st.info(f"Calculated Motor Rating: **{motor_kw:.1f} kW**")
with col2:
    motor_type = st.selectbox("Type of Motor", options=list(motor_type_mult.keys()))
    motor_rpm = st.selectbox("Motor RPM", options=list(motor_rpm_mult.keys()))
with col3:
    motor_protection = st.selectbox("Motor Protection", options=list(motor_protection_mult.keys()))
    needs_vfd = st.radio("VFD Required?", options=["No", "Yes"])

st.divider()

st.subheader("3. Sealing, Mounting & Accessories")
col1, col2, col3 = st.columns(3)
with col1:
    seal_plan = st.selectbox("API Seal Plan", options=list(seal_plan_costs.keys()))
with col2:
    base_plate_weight_kg = st.number_input("Base Plate Weight (kg)", min_value=10.0, value=350.0)
with col3:
    flange_size = st.selectbox("Expansion Bellows Size", options=list(bellows_cost.keys()), index=2)

st.divider()

# --- CALCULATION LOGIC ---
if st.button("Calculate Detailed Cost", type="primary", use_container_width=True):
    
    # 1. Bare Shaft (Includes flow, head, and impeller size coefficient)
    base_frame_cost = (flow * head * 10) + (impeller_dia * 50)
    bare_shaft_cost = base_frame_cost * moc_multipliers[moc] * stages
    
    # 2. Motor Calculation (Base rate x Type x RPM x Protection)
    adjusted_motor_rate = base_motor_rate_per_kw * motor_type_mult[motor_type] * motor_rpm_mult[motor_rpm] * motor_protection_mult[motor_protection]
    motor_cost = motor_kw * adjusted_motor_rate
    
    # 3. Seal Plan
    seal_cost = seal_plan_costs[seal_plan]
    
    # 4. Base Plate
    base_plate_cost = base_plate_weight_kg * base_plate_per_kg
    
    # 5. Accessories (Bellows + Coupling + Guards)
    bellow_price = bellows_cost[flange_size]
    accessories_cost = (bellow_price * 2) + 8500 
    
    # 6. VFD
    vfd_cost = (motor_kw * vfd_rate_per_kw) if needs_vfd == "Yes" else 0

    # Totaling
    sub_total = bare_shaft_cost + motor_cost + seal_cost + base_plate_cost + accessories_cost + vfd_cost
    
    # 15% Margin for Testing, Profit, and Overhead
    overheads = sub_total * 0.15
    final_cost = sub_total + overheads

    # --- RESULTS DISPLAY ---
    st.subheader("📊 Detailed Cost Breakdown")
    c1, c2, c3 = st.columns(3)
    c1.metric("Bare Shaft Pump", f"₹{bare_shaft_cost:,.0f}")
    c2.metric("Motor Cost", f"₹{motor_cost:,.0f}")
    c3.metric("Seal Plan Cost", f"₹{seal_cost:,.0f}")
    
    c4, c5, c6 = st.columns(3)
    c4.metric("Base Plate", f"₹{base_plate_cost:,.0f}")
    c5.metric("Accessories (Bellows, etc.)", f"₹{accessories_cost:,.0f}")
    c6.metric("VFD Panel", f"₹{vfd_cost:,.0f}")

    st.success(f"**Sub-Total:** ₹{sub_total:,.2f}")
    st.info(f"**Testing, Overheads & Margin (15%):** ₹{overheads:,.2f}")
    st.error(f"### **FINAL ESTIMATED COST: ₹{final_cost:,.2f}**")
