#!/usr/bin/env python3
"""Independent synthetic wholesale branch operations generator. No input datasets."""
import csv, json, random, hashlib, argparse, calendar
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict

SEED=20261117
START=date(2025,1,1); DAYS=365
CATEGORIES=['Workshop Essentials','Facility Care','Safety & Protection','Electrical Supplies','Packaging & Storage','Service Equipment']
BRANCHES=['North Branch','South Branch','East Branch','West Branch']

def write(out,name,cols,rows):
    with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
    return len(rows)

def generate(out):
    rng=random.Random(SEED);out.mkdir(parents=True,exist_ok=True)
    counts={}
    def emit(name,cols,rows): counts[name]=write(out,name,cols,rows)
    loc=[dict(location_id=f'B{i}',location_name=n,location_type='branch',region='Fictional Region',capacity_units=6000+i*400) for i,n in enumerate(BRANCHES,1)]
    loc.append(dict(location_id='DC1',location_name='Central Distribution Center',location_type='distribution_center',region='Fictional Region',capacity_units=60000))
    emit('dim_location',list(loc[0]),loc)
    suppliers=[dict(supplier_id=f'S{i:02}',supplier_name=f'Invented Supplier {i:02}',direct_to_branch=int(i%3==0),lead_time_days=3+i%5) for i in range(1,13)]
    emit('dim_supplier',list(suppliers[0]),suppliers)
    products=[];base_cost={};base_price={};velocity={};supplier_by_sku={}
    for i in range(1,121):
        sku=f'FI-{i:04}';cat=CATEGORIES[(i-1)//20];cost=round(rng.uniform(24,540),2);markup=rng.uniform(1.25,1.85)
        supplier=f'S{1+(i-1)%12:02}';base_cost[sku]=cost;base_price[sku]=round(cost*markup,2);velocity[sku]=rng.uniform(.10,1.6)
        supplier_by_sku[sku]=supplier
        products.append(dict(sku=sku,product_name=f'Fictional {cat} Item {i:03}',category=cat,unit='each',supplier_id=supplier,base_unit_cost=cost,list_price=base_price[sku],active_from='2025-01-01'))
    emit('dim_product',list(products[0]),products)
    customers=[]
    for i in range(1,161):
        customers.append(dict(customer_id=f'C{i:04}',customer_name=f'Fictional Account {i:04}',segment=['trade','small_business','institutional','walk_in'][i%4],home_branch=f'B{1+i%4}',account_type='registered' if i<=120 else 'occasional'))
    emit('dim_customer',list(customers[0]),customers)
    dates=[]
    for j in range(DAYS):
        d=START+timedelta(days=j)
        dates.append(dict(date=d.isoformat(),year=d.year,month=d.month,day=d.day,weekday=d.weekday(),month_key=d.strftime('%Y-%m')))
    emit('dim_date',list(dates[0]),dates)
    # Cost is tracked as moving weighted average at each location; all opening stock is valued at invented starting cost.
    qty=defaultdict(int);value=defaultdict(float)
    movements=[];snapshots=[];purchases=[];orders=[];tickets=[];sales=[];demand=[];counts_physical=[]
    incidents=[];ops=[];budgets=[];traffic=[];adjustments=[]
    shelf_snapshots=[];shelf_events=[];shelf_qty=defaultdict(int)
    # Explicitly invented stressed SKU-branch pairs; not calibrated to real stores.
    stressed={(f'B{b}',sku) for b in range(1,5) for i,sku in enumerate(base_cost) if (i+7*b)%5==0}
    shelf_capacity={sku: max(3,round(velocity[sku]*7)+2) for sku in base_cost}
    next_shelf_event=0
    def shelf_fill(ds,branch,sku,kind):
        nonlocal next_shelf_event
        k=(branch,sku);before=shelf_qty[k]
        moved=max(0,min(shelf_capacity[sku]-before,qty[k]-before))
        if moved:
            shelf_qty[k]+=moved;next_shelf_event+=1
            shelf_events.append(dict(event_id=f'SR{next_shelf_event:08}',date=ds,location_id=branch,sku=sku,units_moved=moved,event_type=kind))

    next_movement=0;next_sale=0;next_order=0;next_ticket=0;next_incident=0;next_purchase=0
    pending=defaultdict(list)
    def movement(d,loc,sku,delta,unit_cost,kind,ref):
        nonlocal next_movement
        k=(loc,sku);old=qty[k];oldval=value[k]
        if delta<0:
            if -delta>old: raise AssertionError(('negative inventory',d,loc,sku,old,delta))
            avg=oldval/old if old else 0
            newval=oldval+delta*avg
            cost=avg
        else:
            cost=unit_cost;newval=oldval+delta*cost
        qty[k]=old+delta;value[k]=0 if qty[k]==0 else round(newval,5)
        next_movement+=1
        movements.append(dict(movement_id=f'M{next_movement:08}',date=d,location_id=loc,sku=sku,quantity_change=delta,unit_cost=round(cost,5),movement_type=kind,reference_id=ref))
        return cost
    for sku in base_cost:
        movement('2024-12-31','DC1',sku,240,base_cost[sku],'opening_balance','OPEN')
        for b in range(1,5):movement('2024-12-31',f'B{b}',sku,(9 if (sku in base_cost and (list(base_cost).index(sku)+7*b)%5==0) else 28),base_cost[sku],'opening_balance','OPEN')
    # Ex-ante annual budget: analytically derived from planned footfall, basket and
    # independently invented prices. Never uses realized tickets, sales or inventory.
    # The planning assumptions are explicitly separate from stochastic operations.
    planning_conversion=.52
    planning_basket_lines=sum(n*w for n,w in zip([1,2,3,4,5],[25,32,24,14,5]))/100
    planning_units_per_line=sum(n*w for n,w in zip([1,2,3,4],[50,30,15,5]))/100
    planning_availability=.94
    planning_discount=.035
    planning_avg_unit_price=sum(base_price.values())/len(base_price)
    for month in range(1,13):
        first=date(2025,month,1);ndays=calendar.monthrange(2025,month)[1]
        weekdays=sum((first+timedelta(days=j)).weekday()<5 for j in range(ndays))
        weekends=ndays-weekdays
        for b in range(1,5):
            branch_factor=(1+.07*(b-2))
            seasonal_factor=(1+.12*(month in (6,7,11,12)))
            planned_visits=(46*weekdays+25*weekends)*branch_factor*seasonal_factor
            sales_target=round(planned_visits*planning_conversion*planning_basket_lines*planning_units_per_line*planning_avg_unit_price*planning_availability*(1-planning_discount),2)
            budgets.append(dict(month_key=f'2025-{month:02}',location_id=f'B{b}',sales_budget=sales_target,gross_margin_budget=round(sales_target*.32,2),operating_contribution_budget=round(sales_target*.15,2),budget_version='ex_ante_plan_v2'))
    emit('fact_budget',list(budgets[0]),budgets)
    # Track ordered stock by SKU and branch, without claiming all transfers are instant.
    for day in range(DAYS):
        dt=START+timedelta(days=day);ds=dt.isoformat();month=dt.month
        for event in pending.pop(day,[]):
            typ,loc,sku,n,cost,ref=event
            movement(ds,loc,sku,n,cost,typ,ref)
            if typ=='purchase_receipt':
                next_purchase+=1;purchases.append(dict(receipt_id=f'R{next_purchase:07}',order_id=ref,date=ds,location_id=loc,sku=sku,units_received=n,unit_cost=round(cost,2)))
        # Opening/periodic shelf fills: a shelf stockout can coexist with positive backroom stock.
        for b in range(1,5):
            branch=f'B{b}'
            for sku in base_cost:
                k=(branch,sku)
                shelf_qty[k]=min(shelf_qty[k],qty[k])
                if day==0:
                    shelf_fill(ds,branch,sku,'opening_shelf_fill')
                elif rng.random() < (.53 if k in stressed else .88):
                    shelf_fill(ds,branch,sku,'scheduled_shelf_replenishment')
        # Replenishment: CEDIS orders from suppliers; branches order from CEDIS or direct supplier.
        if day%7==0:
            for sku in base_cost:
                if qty['DC1',sku]<150:
                    next_order+=1;ref=f'PO{next_order:07}';n=210
                    supplier=supplier_by_sku[sku];lead=3+int(supplier[1:])%5
                    cost=round(base_cost[sku]*(1+0.003*(month-1))*(1+rng.uniform(-.015,.015)),2)
                    orders.append(dict(order_id=ref,order_date=ds,source_id=supplier,destination_id='DC1',sku=sku,units_ordered=n,expected_date=(dt+timedelta(days=lead)).isoformat(),order_type='supplier_purchase'))
                    pending[day+lead].append(('purchase_receipt','DC1',sku,n,cost,ref))
                for b in range(1,5):
                    branch=f'B{b}'
                    if qty[branch,sku]>=(7 if (branch,sku) in stressed else 17):continue
                    n=(22 if (branch,sku) in stressed else 35);direct=(int(supplier_by_sku[sku][1:])%3==0)
                    if direct:
                        next_order+=1;ref=f'PO{next_order:07}';lead=3+int(supplier_by_sku[sku][1:])%5+(3 if (branch,sku) in stressed else 0)
                        cost=round(base_cost[sku]*(1+0.003*(month-1))*(1+rng.uniform(-.015,.015)),2)
                        orders.append(dict(order_id=ref,order_date=ds,source_id=supplier_by_sku[sku],destination_id=branch,sku=sku,units_ordered=n,expected_date=(dt+timedelta(days=lead)).isoformat(),order_type='direct_supplier'))
                        pending[day+lead].append(('purchase_receipt',branch,sku,n,cost,ref))
                    elif qty['DC1',sku]>=n:
                        next_order+=1;ref=f'TR{next_order:07}';lead=(5 if (branch,sku) in stressed else 2)
                        avg=value['DC1',sku]/qty['DC1',sku]
                        movement(ds,'DC1',sku,-n,0,'transfer_dispatch',ref)
                        orders.append(dict(order_id=ref,order_date=ds,source_id='DC1',destination_id=branch,sku=sku,units_ordered=n,expected_date=(dt+timedelta(days=lead)).isoformat(),order_type='cedis_transfer'))
                        pending[day+lead].append(('transfer_receipt',branch,sku,n,avg,ref))
        for b in range(1,5):
            branch=f'B{b}';weekend=dt.weekday()>=5
            visits=rng.randint(32,60) if not weekend else rng.randint(15,35)
            visits=int(visits*(1+.07*(b-2))*(1+.12*(month in (6,7,11,12))))
            buyers=0
            for v in range(visits):
                if rng.random()>.52:continue
                buyers+=1;next_ticket+=1;tid=f'T{next_ticket:08}'
                # Repeat registered accounts across days and tickets; occasional accounts are assigned less often.
                cid=f'C{rng.randint(1,120):04}' if rng.random()<.85 else f'C{rng.randint(121,160):04}'
                basket_size=rng.choices([1,2,3,4,5],[25,32,24,14,5])[0]
                skus=rng.sample(list(base_cost),basket_size)
                tickets.append(dict(ticket_id=tid,date=ds,location_id=branch,customer_id=cid,channel='counter' if rng.random()<.8 else 'account_order',ticket_status='attempted_purchase'))
                for sku in skus:
                    requested=rng.choices([1,2,3,4],[50,30,15,5])[0]
                    available=qty[branch,sku];on_shelf=shelf_qty[branch,sku]
                    fulfilled=min(requested,available,on_shelf)
                    # A shelf shortage is distinct from branch inventory exhaustion.
                    shortage_reason=('none' if fulfilled==requested else ('branch_inventory' if available<requested and available<=on_shelf else 'shelf_execution'))
                    shelf_qty[branch,sku]-=fulfilled
                    demand.append(dict(ticket_id=tid,date=ds,location_id=branch,sku=sku,units_requested=requested,units_fulfilled=fulfilled,units_unfulfilled=requested-fulfilled,shortage_reason=shortage_reason))
                    if fulfilled==0:continue
                    discount=.08 if cid<='C0040' else (.035 if fulfilled>=3 else 0)
                    unit_price=round(base_price[sku]*(1+.002*(month-1))*(1-discount),2)
                    unit_cogs=movement(ds,branch,sku,-fulfilled,0,'sale',tid)
                    next_sale+=1
                    sales.append(dict(sale_line_id=f'L{next_sale:08}',ticket_id=tid,date=ds,location_id=branch,customer_id=cid,sku=sku,units=fulfilled,unit_net_price=unit_price,net_sales=round(unit_price*fulfilled,2),unit_cogs=round(unit_cogs,5),net_cogs=round(unit_cogs*fulfilled,2),discount_rate=discount))
            traffic.append(dict(date=ds,location_id=branch,visits=visits,purchasing_visits=buyers,measurement_method='synthetic_counter'))
            if day%13==0:
                next_incident+=1;kind=rng.choice(['customer_complaint','facility_maintenance','training_followup','procedure_exception'])
                incidents.append(dict(incident_id=f'I{next_incident:06}',date_opened=ds,location_id=branch,incident_type=kind,severity=rng.choice(['low','medium','high']),status='closed' if rng.random()<.75 else 'open',days_to_close=rng.randint(1,8)))
            if dt.day==1:
                maint_due=rng.randint(4,9);audit_due=rng.randint(2,6)
                ops.append(dict(month_key=dt.strftime('%Y-%m'),location_id=branch,headcount=8+b,training_hours=rng.randint(8,30),training_completion_rate=round(rng.uniform(.72,.98),3),maintenance_tasks_due=maint_due,maintenance_tasks_completed=rng.randint(0,maint_due),audit_actions_due=audit_due,audit_actions_closed=rng.randint(0,audit_due)))
        # Physical counts on last day of each month: discrepancies are explicit and adjusted in inventory ledger.
        if (dt+timedelta(days=1)).month!=month:
            for b in range(1,5):
                branch=f'B{b}'
                for sku in list(base_cost)[::10]:
                    theoretical=qty[branch,sku];variance=rng.choice([-2,-1,0,0,0,1])
                    physical=max(0,theoretical+variance);variance=physical-theoretical
                    cid=f'CT{month:02}{b}{sku[-4:]}'
                    counts_physical.append(dict(count_id=cid,date=ds,location_id=branch,sku=sku,book_units=theoretical,physical_units=physical,variance_units=variance,reason='count_difference' if variance else 'matched',review_status='reviewed'))
                    if variance:
                        avg=value[branch,sku]/theoretical if theoretical else base_cost[sku]
                        movement(ds,branch,sku,variance,avg,'count_adjustment',cid)
                        shelf_qty[branch,sku]=min(shelf_qty[branch,sku],qty[branch,sku])
        for b in range(1,5):
            branch=f'B{b}'
            for sku in base_cost:
                onhand=qty[branch,sku];shelf=shelf_qty[branch,sku]
                assert 0<=shelf<=onhand
                shelf_snapshots.append(dict(date=ds,location_id=branch,sku=sku,shelf_units=shelf,backroom_units=onhand-shelf,branch_on_hand_units=onhand,shelf_empty=int(shelf==0),branch_empty=int(onhand==0)))
        for locid in ['DC1']+[f'B{i}' for i in range(1,5)]:
            for sku in base_cost:
                snapshots.append(dict(date=ds,location_id=locid,sku=sku,closing_units=qty[locid,sku],closing_inventory_value=round(value[locid,sku],2),moving_avg_unit_cost=round(value[locid,sku]/qty[locid,sku],5) if qty[locid,sku] else 0))
    for name,rows in [('fact_ticket',tickets),('fact_sales',sales),('fact_demand',demand),('fact_traffic',traffic),('fact_purchase_receipt',purchases),('fact_replenishment',orders),('fact_inventory_movement',movements),('fact_inventory_snapshot',snapshots),('fact_physical_count',counts_physical),('fact_incident',incidents),('fact_operations_monthly',ops),('fact_shelf_snapshot',shelf_snapshots),('fact_shelf_replenishment',shelf_events)]:
        emit(name,list(rows[0]),rows)
    # Monthly operating expenses are explicitly invented and not inferred from actual sales.
    expenses=[]
    for month in range(1,13):
        for b in range(1,5):
            for typ,base in [('payroll',43000),('rent',17500),('utilities',6000),('local_marketing',3500),('other_branch_overhead',5000)]:
                expenses.append(dict(month_key=f'2025-{month:02}',location_id=f'B{b}',expense_type=typ,amount=round(base*(1+.04*(b-2))*(1+.005*(month-1)),2),allocation_type='direct_simulated'))
    emit('fact_operating_expense',list(expenses[0]),expenses)
    scenario=[dict(scenario_id='S0',name='baseline',status='not_executed',description='Existing fictional operating policy'),dict(scenario_id='S1',name='commercial_optimization',status='not_executed',description='Candidate price and assortment changes'),dict(scenario_id='S2',name='integrated_optimization',status='not_executed',description='Candidate commercial plus replenishment changes')]
    emit('scenario_parameters',list(scenario[0]),scenario)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.csv'))}
    (out/'checksums.json').write_text(json.dumps(hashes,indent=2)+'\n')
    (out/'manifest.json').write_text(json.dumps(dict(seed=SEED,period='2025-01-01 to 2025-12-31',generator='independent_standard_library_v0.4_availability',source='fully synthetic; no external input files',counts=counts),indent=2)+'\n')
    print(json.dumps(counts,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='data');args=p.parse_args();generate(Path(args.output))