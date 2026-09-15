"""Ratios of configuration-level medians; counter domains remain separate."""
import numpy as np
import pandas as pd

GROUP=['q_old','scenario','gate','product_state','chunk_bytes','io_mode','target','study']

def statistic(values):
    a=pd.Series(values,dtype=float).dropna()
    if not len(a):return {k:np.nan for k in ['median','min','max','std','cv']}
    std=a.std(ddof=1) if len(a)>1 else np.nan
    return dict(median=a.median(),min=a.min(),max=a.max(),std=std,cv=std/a.mean() if a.mean() else np.nan)

def ratio(a,b):
    return a/b if pd.notna(a) and pd.notna(b) and b>0 else np.nan

def summarize(raw):
    raw=raw.copy()
    for domain in ['algorithmic','proc','device']:
        raw[domain+'_traffic_bytes']=raw[domain+'_read_bytes']+raw[domain+'_write_bytes']
    comparisons=[];stats=[]
    fields=['total_elapsed_s','operation_elapsed_s','sync_elapsed_s','cpu_elapsed_s','peak_rss_bytes',
            'pread_calls','pwrite_calls','effective_input_GBps','effective_output_GBps',
            'algorithmic_traffic_bytes','proc_traffic_bytes','device_traffic_bytes',
            'algorithmic_write_bytes','proc_write_bytes','device_write_bytes']
    for key,g in raw.groupby(GROUP,dropna=False):
        meta=dict(zip(GROUP,key));by_policy={}
        for policy,h in g.groupby('policy'):
            record=dict(**meta,policy=policy,repetitions=len(h))
            for field in fields:
                for name,value in statistic(h[field]).items():record[field+'_'+name]=value
            record['device_write_amplification']=ratio(record['device_write_bytes_median'],h.new_state_bytes.iloc[0])
            by_policy[policy]=record;stats.append(record)
        fused='FUSED_BASIS' if meta['scenario']=='basis' else 'PRODUCT_FUSED'
        baselines=['NAIVE_BASIS','THIN_BASIS'] if meta['scenario']=='basis' else ['NAIVE_PRODUCT']
        for baseline in baselines:
            if baseline not in by_policy or fused not in by_policy:continue
            b,f=by_policy[baseline],by_policy[fused]
            row=dict(**meta,old_size_GiB=(16<<int(meta['q_old']))/1024**3,baseline=baseline,fused=fused,
                     baseline_repetitions=b['repetitions'],fused_repetitions=f['repetitions'],
                     interpretation_eligible=min(b['repetitions'],f['repetitions'])>=3)
            for domain in ['algorithmic','proc','device']:
                for method,data in [('baseline',b),('fused',f)]:
                    row[f'{method}_{domain}_traffic_bytes']=data[domain+'_traffic_bytes_median']
                    row[f'{method}_{domain}_write_bytes']=data[domain+'_write_bytes_median']
                row[domain+'_traffic_reduction']=ratio(b[domain+'_traffic_bytes_median'],f[domain+'_traffic_bytes_median'])
                row[domain+'_write_reduction']=ratio(b[domain+'_write_bytes_median'],f[domain+'_write_bytes_median'])
            row.update(baseline_latency_s=b['total_elapsed_s_median'],fused_latency_s=f['total_elapsed_s_median'],
                       latency_speedup=ratio(b['total_elapsed_s_median'],f['total_elapsed_s_median']),
                       baseline_latency_cv=b['total_elapsed_s_cv'],fused_latency_cv=f['total_elapsed_s_cv'],
                       baseline_cpu_s=b['cpu_elapsed_s_median'],fused_cpu_s=f['cpu_elapsed_s_median'],
                       baseline_device_write_amplification=b['device_write_amplification'],
                       fused_device_write_amplification=f['device_write_amplification'])
            comparisons.append(row)
    return pd.DataFrame(comparisons),pd.DataFrame(stats)
