import importlib.util,json,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(repo/'src'))
p=repo/'scripts/physical-pilot/apx-reclaim-windows-linux-v3.py';s=importlib.util.spec_from_file_location('reclaim_gpt',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
plan=json.loads(pathlib.Path('/root/apx-linux-reclaim-faculdade-20261121T144101Z/reclaim-plan.json').read_bytes())
with tempfile.TemporaryDirectory(dir='/var/lib/apx/tmp') as d:
 image=pathlib.Path(d)/'disposable-gpt.img'
 with image.open('wb') as f:f.truncate((plan['before']['lastlba']+34)*512)
 for stage in ['before','after']:
  script=m.gpt_script(plan[stage]).replace(b'/dev/nvme0n1',str(image).encode())
  subprocess.run(['sfdisk','--no-reread',str(image)],input=script,check=True,capture_output=True)
  actual=json.loads(subprocess.check_output(['sfdisk','--json',str(image)]))['partitiontable']
  actual['device']='/dev/nvme0n1'
  for part in actual['partitions']:part['node']=part['node'].replace(str(image),'/dev/nvme0n1p')
  assert m.canonical_layout(actual)==plan[stage],(stage,actual,plan[stage])
 print(json.dumps({'gpt_roundtrip':True,'protected_partitions_identical':[1,2,3,4,8],'pilot_partitions_touched':False}))
