import _common
import gzip
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from htp.loaders import sha256

out=Path('results/figures'); out.mkdir(exist_ok=True)
s=pd.read_csv('results/circuit_summary.csv')
real=s[(~s.source.isin(['generated','synthetic_control']))&(s.n<=64)]
sem=real[real.representation=='semantic']
raw=Path(json.loads(Path('results/manifests/latest_run.json').read_text())['raw_directory'])
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
def save(fig,name):
    fig.savefig(out/(name+'.png'),bbox_inches='tight')
    fig.savefig(out/(name+'.pdf'),bbox_inches='tight')
    plt.close(fig)
def payload(wid,rep):
    with gzip.open(raw/f'{wid}_{rep}.json.gz','rt') as f: return json.load(f)

# Representatives are nearest to the family median, not chosen for largest effects.
fig,axes=plt.subplots(2,3,figsize=(13,7),sharex=True,sharey=True)
representatives=[]
for ax,family in zip(axes.flat,['arithmetic','qft','qaoa','hea','random','grover_oracle']):
    candidates=sem[(sem.family==family)&sem.n.between(20,40)]
    if candidates.empty:
        candidates=s[(s.source=='generated')&(s.family==family)&(s.representation=='semantic')&s.n.between(20,40)]
    idx=(candidates.log2_ideal_gate_reduction-candidates.log2_ideal_gate_reduction.median()).abs().idxmin()
    row=candidates.loc[idx]; representatives.append(row.to_dict())
    for rep,style in [('semantic','-'),('lowered','--')]:
        trace=pd.DataFrame(payload(row.workload_id,rep)['trace'])
        ax.step(trace.normalized_gate_position,trace.q_live/row.n,where='post',linestyle=style,label=rep)
    ax.set_title(f'{family} | n={row.n}\n{row.source}: {Path(row.source_path).name[:45]}',fontsize=9)
    ax.set_ylim(-.03,1.04); ax.grid(alpha=.2)
axes[0,0].legend(); fig.supxlabel('Normalized gate position'); fig.supylabel('q(t) / n')
fig.suptitle('Figure 1 — Representative activation traces (family median selection)')
fig.tight_layout(); save(fig,'figure1_q_traces')
pd.DataFrame(representatives).to_csv(out/'representative_workloads.csv',index=False)

families=sorted(sem.family.unique())
activation=pd.read_csv('results/qubit_activation.csv')
a=activation.merge(real[['workload_id','representation','family','n']],on=['workload_id','representation'])
fig,axes=plt.subplots(1,2,figsize=(14,6),sharey=True)
grid=np.linspace(0,1,201)
for ax,rep in zip(axes,['semantic','lowered']):
    for family in families:
        af=a[(a.family==family)&(a.representation==rep)]
        curves=[]
        for _,g in af.groupby('workload_id'):
            v=g.first_quantum_fraction.dropna().to_numpy()
            curves.append([(v<=x).sum()/len(g) for x in grid])
        if curves: ax.plot(grid,np.mean(curves,axis=0),label=family)
    ax.set_title(rep); ax.set_xlabel('Normalized first-quantumization position'); ax.grid(alpha=.2)
axes[0].set_ylabel('Mean per-circuit fraction of logical qubits ever Q')
axes[1].legend(bbox_to_anchor=(1.02,1),loc='upper left',fontsize=7)
fig.suptitle('Figure 2 — First-quantumization CDF | external n≤64; never-Q stays below 1')
fig.tight_layout(); save(fig,'figure2_activation_cdf')

fig,ax=plt.subplots(figsize=(15,6))
rng=np.random.default_rng(42)
for j,family in enumerate(families):
    for rep,offset,marker in [('semantic',-.15,'o'),('lowered',.15,'x')]:
        g=real[(real.family==family)&(real.representation==rep)]
        ax.scatter(j+offset+rng.uniform(-.08,.08,len(g)),g.ideal_gate_reduction,s=14,marker=marker,alpha=.65,
                   color='tab:blue' if rep=='semantic' else 'tab:orange',label=rep if j==0 else None)
ax.set_yscale('log'); ax.set_xticks(range(len(families)),families,rotation=55,ha='right')
ax.set_ylabel('ideal_gate_hilbert_volume_reduction'); ax.legend(); ax.grid(axis='y',alpha=.2)
ax.set_title('Figure 3 — Every external circuit, n≤64 | includes basis-only circuits; no synthetic/generated')
save(fig,'figure3_reduction_by_family')

p=real.pivot(index='workload_id',columns='representation',values='log2_ideal_gate_reduction').join(sem.set_index('workload_id')[['family','n']])
fig,ax=plt.subplots(figsize=(8,7))
for family,g in p.groupby('family'):
    ax.scatter(g.semantic,g.lowered,s=22,label=family,alpha=.65)
maximum=max(p.semantic.max(),p.lowered.max())
ax.plot([0,maximum],[0,maximum],'k--',linewidth=1,label='y=x')
zoom=ax.inset_axes([.08,.57,.39,.36])
for family,g in p.groupby('family'):
    zoom.scatter(g.semantic,g.lowered,s=9,alpha=.65)
zoom.plot([0,6],[0,6],'k--',linewidth=.7)
zoom.set(xlim=(-.1,6),ylim=(-.1,6),title='Detail: log2 ratios ≤6')
zoom.grid(alpha=.2)
ax.set_xlabel('Semantic log2 ideal gate-volume reduction'); ax.set_ylabel('Aer-lowered log2 ideal gate-volume reduction')
ax.legend(bbox_to_anchor=(1.02,1),loc='upper left',fontsize=7); ax.grid(alpha=.2)
ax.set_title('Figure 4 — Semantic versus current Aer lowering | external n≤64')
save(fig,'figure4_semantic_vs_lowered')

fig,ax=plt.subplots(figsize=(15,6))
for j,family in enumerate(families):
    g=real[(real.family==family)&(real.representation=='lowered')]
    full=g[g.full_materialization_reached]
    never=g[~g.full_materialization_reached]
    ax.scatter(j+rng.uniform(-.18,.18,len(full)),full.first_full_materialization_fraction,s=16,color='tab:blue')
    ax.scatter(j+rng.uniform(-.18,.18,len(never)),np.full(len(never),1.14),s=18,marker='x',color='tab:red')
ax.axhline(1.07,color='gray',linestyle=':',linewidth=1)
ax.set_yticks([0,.25,.5,.75,1,1.14],['0','.25','.5','.75','1','never full'])
ax.set_xticks(range(len(families)),families,rotation=55,ha='right')
ax.set_ylabel('First full materialization fraction')
ax.set_title('Figure 5 — Full materialization timing | lowered external n≤64')
save(fig,'figure5_full_materialization')

q=pd.read_csv('results/qdao_oracle.csv')
q=q[(q.oracle_ok==True)&(~q.source.isin(['generated','synthetic_control']))&q.n.between(20,40)]
fig,axes=plt.subplots(1,2,figsize=(12,5),sharey=True)
for ax,rep in zip(axes,['semantic','lowered']):
    for m,g in q[q.representation==rep].groupby('m'):
        ax.scatter(m+rng.uniform(-.25,.25,len(g)),g.ideal_traffic_reduction,s=15,alpha=.45,color='tab:blue')
        ax.scatter([m],[g.ideal_traffic_reduction.median()],s=60,marker='_',color='black',linewidths=2)
    ax.set_yscale('log'); ax.set_xticks([16,18,20,22,24]); ax.set_xlabel('m (fixed t=2)'); ax.set_title(rep); ax.grid(alpha=.2)
axes[0].set_ylabel('Ideal QDAO traffic-volume reduction')
fig.suptitle('Figure 6 — Static oracle — excludes materialization overhead\nExternal 20–40 qubits; each point one circuit/m; black marker median')
fig.tight_layout(); save(fig,'figure6_qdao_oracle')
Path('results/manifests/figure_hashes.json').write_text(json.dumps({str(p):sha256(p) for p in sorted(out.glob('*'))},indent=2))
print('Six figures saved as PNG and PDF')
