"""Audit three Shorts revisions and extract all caption cards for visual review."""
from pathlib import Path
import hashlib,json,subprocess,importlib.util
Q=Path(__file__).resolve().parent;R=Q.parents[1]
def loadmodule(name):
 spec=importlib.util.spec_from_file_location(name,Q/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
audit=loadmodule('audit');review=loadmodule('extract_review');rows=json.loads((Q/'queue.json').read_text());results=[]
for row in rows:
 if row['order'] not in [8,19,21]:continue
 E=(R/row['manifest']).parent;row['manifest']=str((E/'shorts-manifest-usagi.json').relative_to(R));row['output']=str((E/'final_remotion_shorts_usagi_9x16.mp4').relative_to(R))
 record=json.loads((E/'shorts-usagi-record.json').read_text());assert audit.sha(R/record['horizontalSource'])==record['horizontalSha256']
 result=audit.check(row);assert result['passed'],result;review.one(row)
 result['horizontalSourceUnchanged']=True;result['subjectiveListening']=False
 (E/'shorts-usagi-qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');results.append(result);print(row['title'],'PASS',flush=True)
(Q/'out/usagi-audit-20261015.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
