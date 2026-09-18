"""Small LaTeX table renderer; numbers always come from measured summary CSVs."""
import math


def number(value):
    if value is None or not math.isfinite(float(value)):
        return 'NA'
    value = float(value)
    if value and (abs(value) < .001 or abs(value) >= 1e6):
        mantissa, exponent = f'{value:.2e}'.split('e')
        return rf'${mantissa}\times 10^{{{int(exponent)}}}$'
    return f'{value:.3f}'


def escape(value):
    return str(value).replace('_',r'\_').replace('&',r'\&').replace('%',r'\%')


def latex_table(frame, columns, caption, label):
    lines=[r'\begin{table*}[t]',r'\centering',r'\small',
           r'\caption{'+caption+'}',r'\label{'+label+'}',
           r'\begin{tabular}{l'+'r'*(len(columns)-1)+'}',r'\hline',
           ' & '.join(title for _,title in columns)+r' \\',r'\hline']
    for row in frame.to_dict('records'):
        values=[]
        for key,_ in columns:
            value=row.get(key)
            values.append(escape(value) if key=='family' else str(int(value)) if key=='n' else number(value))
        lines.append(' & '.join(values)+r' \\')
    lines.extend([r'\hline',r'\end{tabular}',r'\end{table*}'])
    return '\n'.join(lines)+'\n'


def phase_a_tables(summary):
    times=latex_table(summary,[('family','Workload'),('n','$n$'),('qdao_wall_time_s','QDAO (s)'),
        ('qthin_wall_time_s','QThin (s)'),('speedup','Speedup')],
        'File-backed end-to-end runtime: medians of three repetitions. Both systems use the same current-Aer state-injection adapter.',
        'tab:qdao-qthin-runtime')
    traffic=summary.copy()
    for method in ['qdao','qthin']:
        traffic[method+'_gib']=traffic[method+'_algorithmic_total_bytes']/2**30
    return times+'\n'+latex_table(traffic,[('family','Workload'),('n','$n$'),('qdao_gib','QDAO (GiB)'),
        ('qthin_gib','QThin (GiB)'),('algorithmic_traffic_reduction','Reduction')],
        'Instrumented state-payload read/write requests. These are not physical SSD bytes.',
        'tab:qdao-qthin-traffic')
