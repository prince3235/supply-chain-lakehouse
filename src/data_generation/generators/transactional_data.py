import pandas as pd
import numpy as np
import random
import uuid

def generate_transactional_data(config, master_data):
    """
    Simulates a day-by-day supply chain ecosystem to generate coherent
    Inventory, Sales, Shipments, and Returns.
    """
    cal_df = master_data['calendar']
    prod_df = master_data['products']
    store_df = master_data['stores']
    wh_df = master_data['warehouses']
    sup_df = master_data['suppliers']
    
    # Pre-compute some structures for fast lookup
    products = prod_df.to_dict('records')
    stores = store_df.to_dict('records')
    warehouses = wh_df.to_dict('records')
    
    # Store current inventory state: (location_id, product_id) -> state dict
    inventory_state = {}
    for s in stores:
        for p in products:
            inventory_state[(s['store_id'], p['product_id'])] = {
                'available': random.randint(50, 200),
                'reserved': 0,
                'reorder_point': random.randint(10, 30),
                'safety_stock': 10,
                'type': 'store',
                'location_id': s['store_id']
            }
            
    # Active shipments: list of dicts
    active_shipments = []
    
    # Historical lists to build DataFrames later
    sales_records = []
    inventory_records = []
    shipments_records = []
    returns_records = []
    
    # Helper: get supplier for a product
    def get_supplier(prod_id):
        s_list = sup_df[sup_df['product_id'] == prod_id]
        if len(s_list) > 0:
            return s_list.iloc[0].to_dict()
        return None

    print("Simulating days...")
    
    for _, day_row in cal_df.iterrows():
        current_date = day_row['date'].date()
        is_weekend = day_row['weekend_flag']
        is_holiday = day_row['holiday_flag']
        
        # 1. Process Arriving Shipments
        arrived_shipments = [s for s in active_shipments if s['actual_delivery_date'] == current_date]
        for s in arrived_shipments:
            s['status'] = 'Delivered'
            # Increase inventory
            inv = inventory_state.get((s['warehouse_id'], s['product_id'])) # Assuming direct to store for simplicity, mapping warehouse_id to store_id in this context
            if inv:
                inv['available'] += s['quantity']
            
            shipments_records.append(s)
            
        active_shipments = [s for s in active_shipments if s['actual_delivery_date'] > current_date]
        
        # 2. Simulate Sales & Inventory changes per store/product
        for s in stores:
            store_id = s['store_id']
            # Store effect: e.g., Flagship sells more
            store_multiplier = 1.5 if s['store_type'] == 'Flagship' else (0.8 if s['store_type'] == 'Express' else 1.0)
            
            for p in products:
                prod_id = p['product_id']
                inv = inventory_state[(store_id, prod_id)]
                
                # Base Demand Calculation
                # ML Learnable features: weekend lift, holiday lift, price elasticity (implied)
                base_prob = config['base_daily_sales_prob'] * store_multiplier
                if p['category'] == 'Food': base_prob *= 1.5
                
                demand = 0
                if random.random() < base_prob:
                    # They want to buy
                    base_qty = random.randint(1, 5)
                    if is_weekend: base_qty = int(base_qty * 1.3)
                    if is_holiday: base_qty = int(base_qty * 2.0)
                    demand = base_qty
                
                sold_qty = 0
                if demand > 0:
                    if inv['available'] >= demand:
                        sold_qty = demand
                    else:
                        sold_qty = inv['available'] # Stockout / partial fulfillment
                    
                    if sold_qty > 0:
                        inv['available'] -= sold_qty
                        
                        # Record Sale
                        tx_id = str(uuid.uuid4())
                        discount = 0.0
                        if random.random() < 0.1: # 10% chance of promotion
                            discount = round(p['selling_price'] * sold_qty * 0.1, 2)
                        
                        sales_records.append({
                            'transaction_id': tx_id,
                            'transaction_timestamp': pd.Timestamp(current_date) + pd.Timedelta(hours=random.randint(8, 20)),
                            'product_id': prod_id,
                            'store_id': store_id,
                            'customer_id': f'CUST-{random.randint(1, 1000):04d}',
                            'quantity': sold_qty,
                            'unit_price': p['selling_price'],
                            'discount_amount': discount,
                            'total_amount': round((p['selling_price'] * sold_qty) - discount, 2),
                            'payment_method': random.choice(['Credit Card', 'Cash', 'Digital Wallet']),
                            'ingestion_timestamp': pd.Timestamp.now(),
                            'source_system': 'POS_V1',
                            'batch_id': 'BATCH-001'
                        })
                        
                        # Simulate Return (2% chance)
                        if random.random() < 0.02:
                            returns_records.append({
                                'return_id': str(uuid.uuid4()),
                                'transaction_id': tx_id,
                                'product_id': prod_id,
                                'store_id': store_id,
                                'return_date': current_date + pd.Timedelta(days=random.randint(1, 14)),
                                'quantity': random.randint(1, sold_qty),
                                'reason': random.choice(['Defective', 'Changed Mind', 'Wrong Item'])
                            })

                # 3. Check Reorder Point
                if inv['available'] <= inv['reorder_point']:
                    # Trigger Shipment if not already pending heavily
                    pending_qty = sum([sh['quantity'] for sh in active_shipments if sh['warehouse_id'] == store_id and sh['product_id'] == prod_id])
                    if inv['available'] + pending_qty <= inv['reorder_point']:
                        supplier = get_supplier(prod_id)
                        if supplier:
                            order_qty = max(supplier['minimum_order_quantity'], 100)
                            lead = supplier['lead_time_days']
                            rel = supplier['reliability_score']
                            
                            # Delay logic based on reliability
                            delay_days = 0
                            if random.random() > rel:
                                delay_days = random.randint(1, 5)
                                
                            exp_date = current_date + pd.Timedelta(days=lead)
                            act_date = exp_date + pd.Timedelta(days=delay_days)
                            
                            new_shipment = {
                                'shipment_id': f'SHP-{str(uuid.uuid4())[:8]}',
                                'supplier_id': supplier['supplier_id'],
                                'product_id': prod_id,
                                'warehouse_id': store_id, # Using store_id directly as destination for simplicity in this model
                                'order_date': current_date,
                                'expected_delivery_date': exp_date,
                                'actual_delivery_date': act_date,
                                'quantity': order_qty,
                                'status': 'In Transit',
                                'delay_days': delay_days
                            }
                            active_shipments.append(new_shipment)

                # 4. Record Inventory Snapshot
                inventory_records.append({
                    'inventory_id': str(uuid.uuid4()),
                    'product_id': prod_id,
                    'store_id': store_id,
                    'warehouse_id': None,
                    'snapshot_timestamp': pd.Timestamp(current_date),
                    'available_quantity': inv['available'],
                    'reserved_quantity': inv['reserved'],
                    'reorder_point': inv['reorder_point'],
                    'safety_stock': inv['safety_stock'],
                    'inventory_value': round(inv['available'] * p['unit_cost'], 2)
                })

    # Cleanup Returns that fall out of bounds
    ret_df = pd.DataFrame(returns_records)
    if not ret_df.empty:
        # Only keep returns within the generated date range
        ret_df = ret_df[ret_df['return_date'] <= pd.Timestamp(config['end_date']).date()]

    return {
        'sales': pd.DataFrame(sales_records),
        'inventory': pd.DataFrame(inventory_records),
        'shipments': pd.DataFrame(shipments_records),
        'returns': ret_df
    }
