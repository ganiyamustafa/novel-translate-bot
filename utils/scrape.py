import requests
import os

from multiprocessing import Pool
from urllib import parse
from groq import Groq
from bs4 import BeautifulSoup, ResultSet, Tag
from typing import Tuple
from utils.enum import TranslateOutputType, NovelSource

groq_client = Groq(
  api_key=os.getenv("GROQ_KEY"),
)

class Scraper():
  def __init__(self):
    self.url = ""
    self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    self.html_content = ""
    self.groq_client = groq_client

  def _request_html_content(self):
    response = requests.get(self.url, headers=self.headers)

    if response.status_code == 200:
      self.html_content = response.text
    else:
      raise ValueError("Failed to retrieve page\nstatus code: ", response.status_code, "\nmessage: ", response.text[:200])

  def set_url(self, url):
    self.url = url
    return self

  def scrape_list_title(self, title: str, source: NovelSource = NovelSource.SYOSETSU) -> ResultSet[Tag]:
    if source == NovelSource.SYOSETSU:
      self.set_url(f"https://yomou.syosetu.com/search.php?search_type=novel&word={title}&button=")._request_html_content()

      soup = BeautifulSoup(self.html_content, "html.parser")
      return soup.select("div.searchkekka_box .novel_h .tl")
    
    if source == NovelSource.KAKUYOMU:
      self.set_url(f"https://kakuyomu.jp/search?q={title}")._request_html_content()

      soup = BeautifulSoup(self.html_content, "html.parser")

      # return none when empty message found
      if soup.select_one("div.EmptyMessage_emptyMessage__Kvdgs"):
        return None

      return soup.select("h3.Heading_size-m___7G0X span.Gap_size-4s__F67Nf a")

    return None

  def scrape_list_chapter(self, title_url: str) -> ResultSet[Tag]:
    self.set_url(title_url)._request_html_content()

    soup = BeautifulSoup(self.html_content, "html.parser")
    return soup.select("div.p-eplist .p-eplist__sublist .p-eplist__subtitle"), soup.select_one(".c-pager__item--next"), soup.select_one(".c-pager__item--before")

  def scrape_story(self, url: str) -> Tuple[Tag, Tag, Tag]:
    self.set_url(f'https://ncode.syosetu.com/{url}')._request_html_content()

    soup = BeautifulSoup(self.html_content, "html.parser")
    return soup.select_one("div.p-novel__body"), soup.select_one("a.c-pager__item--next"), soup.select_one("a.c-pager__item--before")

  def translate(self, data: str, output_type: TranslateOutputType = TranslateOutputType.STRING) -> str | list[str]:
    filtered_datas = [txt for txt in data.split('\n') if txt]
    args_worker = []
    outputs = []

    while filtered_datas:
      untranslated_text = ""

      while len(untranslated_text) <= 1500:
        if not filtered_datas: 
          break

        untranslated_text += filtered_datas.pop(0)

      args_worker.append((untranslated_text, os.getenv("GROQ_KEY")))

    # multiprocessing worker
    with Pool(processes=len(args_worker)) as pool:
      outputs = pool.map(_translate_text_worker, args_worker)

    if output_type == TranslateOutputType.STRING:
      return '\n'.join(outputs)
    elif output_type == TranslateOutputType.LIST_STRING:
      return outputs

def _translate_text_worker(args):
  # Unpack arguments
  untranslated_txt, api_key = args
  
  # Create a new client for each worker process
  from groq import Groq  # Import here to avoid pickling issues
  groq_client = Groq(api_key=api_key)
  
  chat_completion = groq_client.chat.completions.create(
      messages=[
          {
              "role": "user",
              "content": f"Terjemahkan kalimat berikut ke dalam bahasa Indonesia dengan gaya bahasa manusia yang alami, tidak kaku, tidak seperti terjemahan mesin. Pastikan hasilnya enak dibaca dan seolah ditulis oleh penutur asli bahasa Indonesia. Pastikan hasilnya hanya berisi huruf latin tanpa karakter asing seperti kanji atau huruf asing lainnya. Jangan tambahkan penjelasan atau kata apa pun di luar hasil terjemahan. Cukup berikan hasil terjemahannya saja. \n {untranslated_txt}",
          }
      ],
      model="deepseek-r1-distill-llama-70b",
  )

  try:
      if not chat_completion.choices[0].message.content.split("</think>"):
        return _translate_text_worker(args)

      if not chat_completion.choices[0].message.content.split("</think>")[1]:
        return _translate_text_worker(args)

      return chat_completion.choices[0].message.content.split("</think>")[1]
  except IndexError:
    return "[Format Error]"

# translated_text = ""

# while filtered_text:
#   print("start again ", len(filtered_text))
#   untranslated_text = ""

#   while len(untranslated_text) <= 1400:
#     if not filtered_text: 
#       break
    
#     untranslated_text += "\n" + filtered_text.pop(0)

#   chat_completion = client.chat.completions.create(
#       messages=[
#           {
#               "role": "user",
#               "content": f"Terjemahkan dalam bahasa indonesia, buat agar tidak MTL \n {untranslated_text}",
#           }
#       ],
#       model="deepseek-r1-distill-llama-70b",
#   )

#   translated_text += chat_completion.choices[0].message.content.split("</think>")[1]

# print(translated_text)