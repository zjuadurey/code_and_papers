"""Publication artifacts from frozen materialization model outputs only."""
import _materialization_common as common
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from htp.materialization_policy import POLICIES

out = common.OUT
common.check_frozen()
assert json.loads((out/'verification.json').read_text())['status'] == 'PASS'
figdir = out/'figures'
figdir.mkdir(exist_ok=True)
s = pd.read_csv(out/'workload_policy_results.csv')
p = s[s.primary]
d = p[p.policy == 'PRODUCT_FUSED'].copy()
ids = set(d.workload_id)
colors = dict(zip(POLICIES, ['#777777', '#c15137', '#dfac25', '#20768a']))
short = dict(zip(POLICIES, ['Eager', 'Basis rewrite', 'Basis thin', 'Product fused']))
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'savefig.dpi': 180, 'pdf.fonttype': 42})
caption = 'Trace-driven static model — NOT measured SSD traffic'

def save(fig, name):
    fig.savefig(figdir/(name+'.png'), bbox_inches='tight')
    fig.savefig(figdir/(name+'.pdf'), bbox_inches='tight')
    plt.close(fig)

representatives = []
for family in ['arithmetic', 'qft', 'qaoa', 'random', 'grover_oracle', 'state_preparation']:
    group = d[d.family == family].sort_values(['reduction_vs_eager', 'workload_id'])
    if len(group):
        representatives.append(group.iloc[(len(group)-1)//2])
rep = pd.DataFrame(representatives)
rep[['workload_id','source','family','n','reduction_vs_eager']].to_csv(out/'figure_representatives.csv', index=False)
trace = pd.concat([chunk[(chunk.representation == 'lowered') & chunk.workload_id.isin(set(rep.workload_id))]
                   for chunk in pd.read_csv(out/'gate_event_trace.csv', chunksize=100000,dtype={'physical_backing_bytes':str})], ignore_index=True)
fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True, sharey=True)
for ax, row in zip(axes.flat, representatives):
    t = trace[trace.workload_id == row.workload_id]
    x = t.normalized_gate_position
    ax.step(x, t.q_logical/row.n, where='post', color='#333333', lw=2.8, label='Logical quantumized')
    ax.step(x, t.q_physical_basis_thin/row.n, where='post', color=colors['BASIS_THIN'], ls='--', lw=1.8, label='Basis physical')
    ax.step(x, t.q_physical_product_fused/row.n, where='post', color=colors['PRODUCT_FUSED'], lw=1.6, label='Product physical')
    ax.set_title(f'{row.family}, n={row.n}\n{row.workload_id}', fontsize=9)
    ax.set_ylim(-.03, 1.03)
    ax.grid(alpha=.18)
axes[0,0].legend(fontsize=8, loc='lower right')
for ax in axes[-1,:]: ax.set_xlabel('Normalized gate position')
for ax in axes[:,0]: ax.set_ylabel('q / n')
fig.suptitle('Logical quantumization and physicalization — lowered circuits')
fig.tight_layout()
save(fig, 'fig1_dimensions')

wide = p.pivot(index='workload_id', columns='policy', values='predicted_total_bytes').astype(float)
fig, ax = plt.subplots(figsize=(7,6))
families = sorted(d.family.unique())
cmap = plt.get_cmap('tab20')
for j, family in enumerate(families):
    group = d[d.family == family]
    w = wide.loc[group.workload_id]
    ax.scatter(w.BASIS_THIN, w.PRODUCT_FUSED, s=30, alpha=.8, label=family, color=cmap(j%20))
lo, hi = wide[['BASIS_THIN','PRODUCT_FUSED']].min().min()*.7, wide[['BASIS_THIN','PRODUCT_FUSED']].max().max()*1.4
ax.plot([lo,hi], [lo,hi], '--', color='grey', label='y = x')
ax.set(xscale='log', yscale='log', xlim=(lo,hi), ylim=(lo,hi),
       xlabel='BASIS_THIN predicted total bytes', ylabel='PRODUCT_FUSED predicted total bytes',
       title=f'{len(wide)} common-valid 20–40q lowered circuits, m=16\n{caption}')
ax.legend(bbox_to_anchor=(1.02,1), loc='upper left', fontsize=8)
ax.grid(alpha=.18)
save(fig, 'fig2_thin_vs_product')

fig, ax = plt.subplots(figsize=(12,6))
order = d.groupby('family').reduction_vs_eager.median().sort_values().index
for j, family in enumerate(order):
    g = d[d.family == family].sort_values('workload_id')
    offsets = np.linspace(-.2,.2,len(g)) if len(g)>1 else np.array([0.])
    for eventful, marker, fill in [(True, 'o', True), (False, 's', False)]:
        mask = (g.materialization_events > 0).to_numpy() == eventful
        ax.scatter((j+offsets)[mask], g.reduction_vs_eager.to_numpy()[mask], marker=marker,
                   facecolors=colors['PRODUCT_FUSED'] if fill else 'none', edgecolors=colors['PRODUCT_FUSED'], s=35)
    ax.plot([j-.27,j+.27], [g.reduction_vs_eager.median()]*2, color='black', lw=1.4)
ax.scatter([],[],marker='o',color=colors['PRODUCT_FUSED'],label='At least one physicalization event')
ax.scatter([],[],marker='s',facecolors='none',edgecolors=colors['PRODUCT_FUSED'],label='No physicalization event')
ax.axhline(1,color='grey',ls='--')
ax.set(yscale='log', ylabel='Predicted total byte reduction vs EAGER_FULL',
       title=f'PRODUCT_FUSED: individual primary circuits and family medians\n{caption}')
ax.set_xticks(range(len(order)), order, rotation=45, ha='right')
ax.legend(fontsize=8)
ax.grid(axis='y',alpha=.18)
save(fig, 'fig3_family_reduction')

life = pd.read_csv(out/'qubit_lifetimes.csv')
l = life[(life.representation == 'lowered') & life.workload_id.isin(ids) & ~life.never_quantumized]
fig, ax = plt.subplots(figsize=(8,5))
for j, family in enumerate(sorted(l.family.unique())):
    g = l[l.family == family]
    values = np.sort(g.loc[~g.never_physicalized, 'virtual_product_window_fraction'].to_numpy())
    x = np.r_[0,values,1.]
    y = np.r_[0,np.arange(1,len(values)+1)/len(g),len(values)/len(g)]
    ax.step(x,y,where='post',label=f'{family} ({len(values)}/{len(g)} completed)',color=cmap(j%20))
ax.set(xlabel='Quantumization → physicalization delay / gate count',
       ylabel='Completed lifetimes / all quantumized qubits',ylim=(0,1.02),xlim=(0,1),
       title='Virtual-product lifetime sub-CDF — right-censored qubits stay in denominator')
ax.legend(bbox_to_anchor=(1.02,1),loc='upper left',fontsize=8)
ax.grid(alpha=.18)
save(fig, 'fig4_product_lifetimes')

events = pd.read_csv(out/'physicalization_events.csv')
ep = events[(events.representation == 'lowered') & events.workload_id.isin(ids)]
batch = ep.groupby(['policy','materialization_batch_size']).size()
ks = sorted(ep.materialization_batch_size.unique())
fig, ax = plt.subplots(figsize=(8,5))
for j, policy in enumerate(POLICIES[1:]):
    counts = [batch.get((policy,k),0) for k in ks]
    ax.bar(np.arange(len(ks))+(j-1)*.25,counts,width=.25,label=short[policy],color=colors[policy])
ax.set_xticks(range(len(ks)),ks)
ax.set(xlabel='New physical dimensions per event (k)',ylabel='Number of events',yscale='log',
       title='Materialization batches — primary lowered circuits')
ax.legend(); ax.grid(axis='y',alpha=.18)
save(fig,'fig5_batch_sizes')

# Each panel has its own byte scale: do not conceal small workloads behind a large one.
fig, axes = plt.subplots(2,3,figsize=(13,8))
for ax, row in zip(axes.flat,representatives):
    g = p[p.workload_id == row.workload_id].set_index('policy').loc[list(POLICIES)]
    traversal = g.predicted_qdao_bytes.astype(float).to_numpy()
    materialization = g.predicted_materialization_bytes.astype(float).to_numpy()
    ax.bar(range(4), traversal, label='QDAO traversal', color='#6e9caf')
    ax.bar(range(4), materialization, bottom=traversal, label='Materialization checkpoint',color='#d38a59')
    ax.set_yscale('log')
    positive_components=np.r_[traversal[traversal>0],materialization[materialization>0]]
    totals=traversal+materialization
    ax.set_ylim(positive_components.min()*.45,totals.max()*2.5)
    for x,total in enumerate(totals):
        ax.annotate(f'{total:.2g}',(x,total),xytext=(0,4),textcoords='offset points',ha='center',fontsize=7)
    ax.set_xticks(range(4),[short[x] for x in POLICIES],rotation=28,ha='right',fontsize=8)
    ax.set_title(f'{row.family}, n={row.n}',fontsize=10)
    ax.set_ylabel('Predicted bytes')
axes[0,0].legend(fontsize=7)
fig.suptitle(f'Traversal + materialization composition\n{caption}')
fig.tight_layout()
save(fig,'fig6_traffic_breakdown')

fig, ax = plt.subplots(figsize=(8,5))
for j, policy in enumerate(POLICIES[1:]):
    g = ep[ep.policy == policy].sort_values(['workload_id','gate_index'])
    # Deterministic jitter; every event appears, including identical byte values.
    jitter = .24*np.sin(np.arange(len(g))*2.3999632297)
    ax.scatter(j+jitter,g.write_bytes.astype(float),s=8,alpha=.2,color=colors[policy])
    ax.plot([j-.3,j+.3],[g.write_bytes.astype(float).median()]*2,color='black',lw=2)
ax.set_xticks(range(3),[short[x] for x in POLICIES[1:]])
ax.set(yscale='log',ylabel='Output bytes written per materialization event',
       title=f'Individual events; event sets differ across policies\n{caption}')
ax.text(.02,.02,'Thin ZERO insertion itself writes 0 bytes; dots include dense gate output.',transform=ax.transAxes,fontsize=9)
ax.grid(axis='y',alpha=.18)
save(fig,'fig7_event_writes')

common.check_frozen()
print(f'Wrote seven PNG/PDF figure pairs to {figdir}')
