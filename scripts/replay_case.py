"""Deterministic chronological replay of synthetic P02 v0.4, no future lookahead.
Events per day: inbound receipts; scheduled shelf fills; baseline dispatches;
extra shelf fill; customer ticket lines; physical count adjustments; extra dispatch.
Baseline exact-match verification against P02 closing snapshots is mandatory.
"""
import argparse
from collections import defaultdict, deque
from bisect import bisect_left
from pathlib import Path
import pandas as pd

BRANCHES=('B1','B2','B3','B4')

def load(path):
    return {name:pd.read_csv(path/(name+'.csv')) for name in ['fact_inventory_movement','fact_shelf_replenishment','fact_demand','fact_sales','fact_inventory_snapshot','fact_shelf_snapshot','dim_product','fact_replenishment']}

def run(data:Path,out:Path,extra_fill=3,extra_dispatch=4,lead_days=2,reserve=30):
    out.mkdir(parents=True,exist_ok=True)
    d=load(data); moves=d['fact_inventory_movement']; demand=d['fact_demand']; dates=sorted(d['fact_inventory_snapshot'].date.unique());skus=d['dim_product'].sku.tolist()
    initial=moves[moves.movement_type=='opening_balance']; opening={(r.location_id,r.sku):int(r.quantity_change) for r in initial.itertuples(index=False)}
    # Baseline transfer commitments are known orders, not future demand.
    # Reserve stock for every ordinary dispatch until the next confirmed DC purchase receipt.
    dc_events=defaultdict(list)
    for r in moves[(moves.location_id=='DC1') & (moves.movement_type.isin(['transfer_dispatch','purchase_receipt']))].itertuples(index=False):
        dc_events[r.sku].append((r.date,r.movement_type,abs(int(r.quantity_change))))
    orders=d['fact_replenishment']; order_dates=dict(zip(orders.order_id,orders.order_date))
    # A commitment is visible only after its order creation date.
    confirmed=defaultdict(list)
    for r in moves[(moves.location_id=='DC1') & (moves.movement_type=='transfer_dispatch')].itertuples(index=False):
        if r.reference_id not in order_dates: raise AssertionError('Dispatch without dated order')
        if order_dates[r.reference_id]>r.date: raise AssertionError('Order created after dispatch')
        confirmed[r.sku].append((r.date,order_dates[r.reference_id],-int(r.quantity_change)))
    commitments={}
    for s,events in dc_events.items():
        events.sort(key=lambda x:x[0])
        for day in dates:
            need=0
            for dispatch_day,created_day,q in confirmed.get(s,[]):
                if dispatch_day>day and created_day<=day:need+=q
            commitments[(day,s)]=need
    # Validate baseline transfers end-to-end by reference ID and SKU.
    dispatch=moves[moves.movement_type=='transfer_dispatch'].groupby(['reference_id','sku']).quantity_change.sum().mul(-1)
    arrivals=moves[moves.movement_type=='transfer_receipt'].groupby(['reference_id','sku']).quantity_change.sum()
    in_transit=dispatch.subtract(arrivals,fill_value=0)
    if (in_transit<0).any():
        raise AssertionError('Receipt without corresponding dispatch')
    outstanding_baseline=int(in_transit.sum())
    # Preserve original row order for intraday tickets and same-day movement events.
    mov_by=defaultdict(list)
    for r in moves[moves.movement_type!='opening_balance'].itertuples(index=False):mov_by[r.date].append(r)
    fill_by=defaultdict(list)
    for r in d['fact_shelf_replenishment'].itertuples(index=False):fill_by[r.date].append(r)
    demand_by=defaultdict(list)
    for r in demand.itertuples(index=False):demand_by[r.date].append(r)
    price={}
    for r in d['fact_sales'].itertuples(index=False):price[(r.ticket_id,r.sku)]=(float(r.unit_net_price),float(r.unit_cogs))
    prod=d['dim_product'].set_index('sku')
    # Strict chronological pricing: no discounts from later lines of the same ticket.
    sale_discounts={(r.ticket_id,r.sku):float(r.discount_rate) for r in d['fact_sales'].itertuples(index=False)}
    last_discount=defaultdict(float)
    # Moving-average cost is read from prior-day close, never future close.
    snap=d['fact_inventory_snapshot']; cost_by_day=defaultdict(dict)
    for r in snap.itertuples(index=False):cost_by_day[r.date][(r.location_id,r.sku)]=float(r.moving_avg_unit_cost)
    default_econ={s:(float(r.list_price),float(r.base_unit_cost)) for s,r in prod.iterrows()}
    baseline_stock=opening.copy();cf_stock=opening.copy()
    # Moving-average counterfactual inventory ledger. Costs are carried at event time.
    opening_cost={(r.location_id,r.sku):float(r.unit_cost) for r in initial.itertuples(index=False)}
    cf_value={k:round(q*opening_cost[k],6) for k,q in opening.items()}
    value_events=[];base_shelf=defaultdict(int);cf_shelf=defaultdict(int)
    pending=defaultdict(list); outstanding=defaultdict(int);history=defaultdict(lambda:deque(maxlen=7))
    detail=[]; ledger=[];checks=[];baseline_diff=0; cost_prev={}; adjustment_conflicts=0; extra_units=0; lost_baseline=0; extra_ship=0;baseline_dispatch_shortfall=0
    # Dispatch and purchase events are embedded in movement ledger, and shelf replenishment is separately recorded.
    # P02 generator sequence: arrivals -> fills -> baseline dispatch -> tickets -> count adjustments.
    for i,date in enumerate(dates):
        events=mov_by[date]
        for r in events:
            if r.movement_type not in ('purchase_receipt','transfer_receipt'):continue
            k=(r.location_id,r.sku);q=int(r.quantity_change);baseline_stock[k]+=q;cf_stock[k]+=q
            value_in=q*float(r.unit_cost);cf_value[k]+=value_in
            value_events.append((date,*k,'receipt',q,round(value_in,6),round(cf_value[k],6)))
        for b,s,q in pending.pop(date,[]):
            cf_stock[(b,s)]+=q;outstanding[(b,s)]-=q;ledger.append((date,b,s,'extra_arrival',q))
        for r in fill_by[date]:
            k=(r.location_id,r.sku);q=int(r.units_moved)
            # Baseline events are not automatically feasible in counterfactual; refill as much as possible.
            base_shelf[k]+=q
            cf_shelf[k]+=min(q,max(0,cf_stock[k]-cf_shelf[k]))
        for r in events:
            if r.movement_type!='transfer_dispatch':continue
            k=(r.location_id,r.sku);q=-int(r.quantity_change)
            baseline_stock[k]-=q
            available=cf_stock[k]
            if available<q:baseline_dispatch_shortfall+=q-available
            dispatched=min(q,available)
            c=cf_value[k]/available if available else 0
            cf_value[k]-=dispatched*c;cf_stock[k]-=dispatched
            value_events.append((date,*k,'transfer_dispatch',-dispatched,round(-dispatched*c,6),round(cf_value[k],6)))
            if cf_stock[k]<0:raise AssertionError('negative CEDIS')
        # Policy: extra refill before first ticket; uses current backroom only.
        if extra_fill:
            for b in BRANCHES:
                for s in skus:
                    k=(b,s);refill=min(extra_fill,max(0,cf_stock[k]-cf_shelf[k]))
                    cf_shelf[k]+=refill
                    if refill:ledger.append((date,b,s,'extra_shelf_fill',refill))
        requested_today=defaultdict(int)
        for r in demand_by[date]:
            k=(r.location_id,r.sku);req=int(r.units_requested);requested_today[k]+=req
            # Baseline replay must reproduce exact fulfilled units.
            bqty=min(req,baseline_stock[k],base_shelf[k]);expected=int(r.units_fulfilled)
            if bqty!=expected:
                raise AssertionError(f'Baseline replay mismatch {date} {k}: {bqty} vs {expected}')
            baseline_stock[k]-=bqty;base_shelf[k]-=bqty
            # Evaluate price before updating the observed discount for this line.
            observed_discount=last_discount[k]
            if (r.ticket_id,r.sku) in sale_discounts:
                observed_discount=sale_discounts[(r.ticket_id,r.sku)]
            cqty=min(req,cf_stock[k],cf_shelf[k])
            avg_cost=cf_value[k]/cf_stock[k] if cf_stock[k] else default_econ[r.sku][1]
            sale_cogs=cqty*avg_cost
            cf_value[k]-=sale_cogs;cf_stock[k]-=cqty;cf_shelf[k]-=cqty
            if cf_stock[k]==0:cf_value[k]=0.0
            if cqty:value_events.append((date,*k,'sale',-cqty,round(-sale_cogs,6),round(cf_value[k],6)))
            if (r.ticket_id,r.sku) in sale_discounts:last_discount[k]=observed_discount
            delta=cqty-bqty
            if delta:
                if (r.ticket_id,r.sku) in price:
                    p,_=price[(r.ticket_id,r.sku)]
                    c=avg_cost
                else:
                    # Same-ticket discount is observable at the time of this transaction.
                    p=round(default_econ[r.sku][0]*(1-observed_discount),2)
                    c=avg_cost
                # Synthetic counterfactual: not an observed transaction price.
                rev=delta*p;gp=delta*(p-c);cost=max(delta,0)*(2.5+max(0,p-c)*.12)
                detail.append((date,r.location_id,r.sku,r.ticket_id,req,bqty,cqty,delta,round(rev,2),round(gp,2),round(cost,2),round(gp-cost,2)))
                if delta>0:extra_units+=delta
                else:lost_baseline-=delta
        for r in events:
            if r.movement_type!='count_adjustment':continue
            k=(r.location_id,r.sku);q=int(r.quantity_change)
            baseline_stock[k]+=q
            # Physical count differences belong to baseline observation, not to a new
            # counterfactual physical count. Exclude, disclose, and never clip.
            adjustment_conflicts+=1
            ledger.append((date,r.location_id,r.sku,'baseline_count_adjustment_excluded',q))
            base_shelf[k]=min(base_shelf[k],baseline_stock[k])
        # Validate baseline exact daily snapshots; also cf stock is nonnegative.
        for r in d['fact_inventory_snapshot'].loc[d['fact_inventory_snapshot'].date==date].itertuples(index=False):
            k=(r.location_id,r.sku)
            if baseline_stock[k]!=int(r.closing_units):raise AssertionError(f'Baseline stock mismatch {date} {k}')
            if cf_stock[k]<0:raise AssertionError(f'Negative counterfactual {date} {k}')
        for r in d['fact_shelf_snapshot'].loc[d['fact_shelf_snapshot'].date==date].itertuples(index=False):
            k=(r.location_id,r.sku)
            if base_shelf[k]!=int(r.shelf_units):raise AssertionError(f'Baseline shelf mismatch {date} {k}')
            if not 0<=cf_shelf[k]<=cf_stock[k]:raise AssertionError(f'Invalid counterfactual shelf {date} {k}')
        cost_prev.update(cost_by_day[date])
        # Policy orders AFTER today's tickets and observations. No future stock/sales read.
        if i+lead_days<len(dates):
            for b in BRANCHES:
                for s in skus:
                    k=(b,s);past=history[k]
                    trailing=(sum(past)+requested_today[k])/(len(past)+1)
                    target=max(6,round(trailing*4));gap=target-cf_stock[k]-outstanding[k]
                    if gap<=0:continue
                    avail=max(0,cf_stock[('DC1',s)]-max(reserve,commitments.get((date,s),0)))
                    q=min(extra_dispatch,int(gap),avail)
                    if q:
                        cf_stock[('DC1',s)]-=q;pending[dates[i+lead_days]].append((b,s,q));outstanding[k]+=q
                        ledger.append((date,'DC1',s,'extra_dispatch',-q));extra_ship+=q
        for k,qty in requested_today.items():history[k].append(qty)
        checks.append((date,min(cf_stock.values()),min(cf_shelf.values()),sum(outstanding.values())))
        for k,q in cf_stock.items():
            if cf_value[k]<-0.00001:raise AssertionError(f'Negative inventory value {date} {k}: {cf_value[k]}')
            if q==0 and abs(cf_value[k])>0.00001:raise AssertionError(f'Value with zero units {date} {k}')
    if sum(outstanding.values()):raise AssertionError('outstanding at end')
    df=pd.DataFrame(detail,columns=['date','location_id','sku','ticket_id','requested','baseline_fulfilled','policy_fulfilled','delta_units','incremental_sales','incremental_gross_profit','incremental_handling_cost','incremental_contribution'])
    lg=pd.DataFrame(ledger,columns=['date','location_id','sku','event','quantity_change'])
    ch=pd.DataFrame(checks,columns=['date','min_on_hand','min_shelf','outstanding_units'])
    summary=df.groupby('location_id',as_index=False)[['delta_units','incremental_sales','incremental_gross_profit','incremental_handling_cost','incremental_contribution']].sum()
    val=pd.DataFrame(value_events,columns=['date','location_id','sku','event','quantity_change','value_change','closing_value'])
    val.to_csv(out/'counterfactual_value_events.csv',index=False)
    for fn,obj in [('ticket_deltas.csv',df),('intervention_ledger.csv',lg),('daily_checks.csv',ch),('branch_summary.csv',summary)]:obj.to_csv(out/fn,index=False)
    totals={'extra_fulfilled_units':extra_units,'baseline_sales_displaced_units':lost_baseline,'net_units':extra_units-lost_baseline,'expedited_dispatched_units':extra_ship,'incremental_sales':round(float(df.incremental_sales.sum()),2),'incremental_contribution':round(float(df.incremental_contribution.sum()),2),'baseline_daily_snapshot_checks':'PASS','negative_stock_checks':'PASS','baseline_dispatch_shortfall_units':baseline_dispatch_shortfall,'baseline_transfer_reconciliation':'PASS (including year-end in-transit)','baseline_in_transit_units_at_year_end':outstanding_baseline,'reservation_policy':'only dated orders confirmed by decision date; conservative minimum reserve','baseline_count_adjustments_excluded_from_counterfactual':adjustment_conflicts,'intraday_ordering':'declared synthetic generator order; timestamps unavailable','counterfactual_closing_inventory_value':round(sum(cf_value.values()),2),'counterfactual_valuation':'moving-average event ledger; baseline count adjustments excluded; unit costs from synthetic receipts'}
    import json
    (out/'run_summary.json').write_text(json.dumps(totals,indent=2))
    print(totals);return totals

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--extra-fill',type=int,default=3);p.add_argument('--extra-dispatch',type=int,default=4);p.add_argument('--reserve',type=int,default=30)
    a=p.parse_args();run(a.data,a.output,a.extra_fill,a.extra_dispatch,reserve=a.reserve)
