"""Local English coursework demonstration: trained MLP prediction + exact verification."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
from pathlib import Path

import pandas as pd

from .data import HERE
from .predict import predict


def examples():
    frame=pd.read_csv(HERE/"results/test_predictions.csv")
    selected=[]
    for name,mask in [("SAT example",frame.satisfiable==1),("UNSAT example",frame.satisfiable==0),
                      ("An observed model error",frame.satisfiable!=frame.mlp_prediction)]:
        row=frame[mask].iloc[0]
        selected.append({"name":name,"id":row.instance_id,"n":int(row.n),"clauses":json.loads(row.clauses_json)})
    return selected


class Handler(BaseHTTPRequestHandler):
    def send(self,status,data,content_type="application/json"):
        body=json.dumps(data).encode() if content_type=="application/json" else data
        self.send_response(status);self.send_header("Content-Type",content_type)
        self.send_header("Content-Length",str(len(body)));self.send_header("Cache-Control","no-store")
        self.end_headers();self.wfile.write(body)

    def do_GET(self):
        if self.path=="/":self.send(200,(HERE/"index.html").read_bytes(),"text/html; charset=utf-8")
        elif self.path=="/api/data":self.send(200,{"examples":examples(),"metrics":json.loads((HERE/"results/metrics.json").read_text())})
        else:self.send(404,{"error":"Not found"})

    def do_POST(self):
        if self.path!="/api/predict":self.send(404,{"error":"Not found"});return
        origin=self.headers.get("Origin")
        if origin and urlparse(origin).netloc!=self.headers.get("Host"):
            self.send(403,{"error":"Local same-origin requests only"});return
        try:
            length=int(self.headers.get("Content-Length",0))
            if not 0<length<=8192 or self.headers.get_content_type()!="application/json":raise ValueError("Expected bounded JSON")
            value=json.loads(self.rfile.read(length))
            if type(value) is not dict:raise ValueError("JSON object required")
            result=predict(value.get("n"),value.get("clauses"))
        except (ValueError,TypeError) as exc:self.send(400,{"error":str(exc)});return
        except Exception as exc:self.send(500,{"error":f"{type(exc).__name__}: {exc}"});return
        self.send(200,result)


if __name__=="__main__":
    print("CA6000 SAT demo: http://127.0.0.1:8766 | Ctrl+C to stop",flush=True)
    server=HTTPServer(("127.0.0.1",8766),Handler)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
