# %%
from typing import Union, List, Dict
from tqdm.auto import tqdm
import pandas as pd
from pathlib import Path
import arxiv
from os import system as system_command
import time
import datetime
import requests


from utils.color_log import color, tracing_log
logging = color.setup(name=__name__, level=color.DEBUG)
# arxiv.logging.basicConfig(level=arxiv.logging.DEBUG)

PATH_ALL_PAPER_TRAIN: str = "../sota/dataset/train"
PATH_ALL_PAPER_VALIDATION: str = "../sota/dataset/validation"

PATH_TO_DOWNLOAD: str = r"sources"

all_paper_id_iter = Path(PATH_ALL_PAPER_TRAIN).glob("*")

# %%

# %%
# process_cnt = 10000
# # process_cnt_bak = process_cnt
# process_cnt_bak = process_cnt
# '''Will replaced by len() method later.'''

all_paper_dict: dict = {}
for paper_src in all_paper_id_iter:
  all_paper_dict[paper_src.name] = {} # {"name": None, "title": None}
  # all_paper_dict[paper_src.name]["name"] = paper_src.name
  
  # process_cnt -= 1
  # if process_cnt == 0:
  #   break
  
process_cnt_bak = len(all_paper_dict.keys())

# %%
def checkAndCreateFolder(dirpath: str,
                         filename: str=None, 
                         basepath: str="sources",
                         demo: bool=False
                        ) -> bool:
  '''
  return `True` if the file exists.
  '''
  base_path = Path(basepath)
  folder_path = Path(basepath).joinpath(dirpath)
  file_path = folder_path.joinpath(filename)
  if not base_path.exists():
    base_path.mkdir()
  if not folder_path.exists():
    logging.warning(f"['{folder_path}'] doesn't exist. ", end="" if not demo else "\n")
    if not demo:
      logging.info("Creating one for you...")
      folder_path.mkdir()
  else:
    if demo:
      logging.info(f"['{folder_path}'] does exist!")
  
  if file_path.exists():
    return_code = system_command(f"gunzip -t '{file_path}' > /dev/null")
    if return_code:
      logging.error(f"Error {return_code}. Removing corrupted file ('{file_path}'). Please run the download process later.")
      system_command(f"rm {file_path}")

  return file_path.exists()

def download_source_safe(dirpath: str="./",
                         filename: str=""
                         ) :
  '''
  Downloads the source tarfile for this result to the specified directory.\n
  Please take `filename` as `arxiv_id`. (e.g., 1112.0097v1)
  
  This is the improvement for the `download_source` in `arxiv` package.
  '''
  
  base_url = "https://arxiv.org/src/"
  response = requests.get(base_url + filename)
  
  download_to_path = Path(dirpath).joinpath(filename) if filename != "" \
    else response.headers["content-disposition"].split("filename=")[-1].strip("\"")
  with open(download_to_path, "wb") as file:
    file.write(response.content)
  
  return str(download_to_path.absolute())

# _paper_src_name = "2005.05005v2"
# _paper_src_name = "2206.09112v4"
# checkAndCreateFolder(dirpath=_paper_src_name.split(".")[0], filename=_paper_src_name, demo=True)

# %%
def download_src(arxiv_id: list, 
                 basepath: str="sources"
                 ) -> dict:
  '''
  Check if the directory exists, using arXiv API to download the `src`(latex included).
  
  ## returns
  paper_info: dict
  '''
  search_by_id = arxiv.Search(id_list=arxiv_id)
  client = arxiv.Client(page_size=400, delay_seconds=3, num_retries=3)
  pbar = tqdm(client.results(search_by_id), 
              total=len(arxiv_id),
              miniters=1,
              mininterval=0,
              desc="Starting process..."
              )
  skipped_list = []
  paper_info: dict = {}
  timer_main = tracing_log.Timer(start_time=time.time())

  for paper in pbar: 
    timer_sub = tracing_log.Timer(start_time=time.time())
    paper_id = paper.get_short_id()
    pbar.set_description(f"Processing {paper_id}")
    paper_info[paper_id] = {}
    paper_info[paper_id]["name"] = paper_id
    paper_info[paper_id]["title"] = paper.title
    if not checkAndCreateFolder(dirpath=paper_id.split(".")[0], filename=paper_id, basepath=PATH_TO_DOWNLOAD):
      # Skip the task if the file already exist.
      # paper.download_source(dirpath=Path(basepath).joinpath(paper_id.split(".")[0]), filename=paper_id)
      download_source_safe(dirpath=Path(basepath).joinpath(paper_id.split(".")[0]), filename=paper_id)
      # pbar.write(f"({timer_sub.update(show_float=1)}) {pbar.n+1}: [{paper_id}] {paper.title}")
      log_str = f"[{datetime.datetime.now()}] ({timer_sub.update(show_float=1)}) {pbar.n+1}: [{paper_id}] {paper.title}"
      pbar.write(log_str)
      with open("arxiv_download.log", "a") as logfile:
        logfile.write(f"{log_str}\n")
    else:
      skipped_list.append(paper_id)

  pbar.write(f"({len(skipped_list)}/{len(arxiv_id)} were skipped) (time_span={timer_main.update(show_float=1)})")

  return paper_info

# %%
RECORD_FMT: str = "csv"
ITER_STEP: int = 400
start_flag: int = 0

while start_flag <= process_cnt_bak:
  if start_flag + ITER_STEP >= process_cnt_bak:
    probe_interval = slice(start_flag, process_cnt_bak)
  else:
    probe_interval = slice(start_flag, start_flag + ITER_STEP)
  paper_id_list = list(all_paper_dict.keys())[probe_interval]
  logging.info(f"===== Crawler Interval: [{probe_interval.start}, {probe_interval.stop}] Total: {process_cnt_bak} =====")
  part_paper_dict = download_src(arxiv_id=paper_id_list, basepath=PATH_TO_DOWNLOAD)
  start_flag += ITER_STEP

  info_table = pd.DataFrame(part_paper_dict).T
  info_table.to_csv(f"record_{probe_interval.start}-{probe_interval.stop}.{RECORD_FMT}")
  
logging.info(f"Done.")

# %%



