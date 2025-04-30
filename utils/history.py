import json
import aiofiles
import os
from datetime import datetime
from bs4 import Tag
from utils.enum import NovelSource

class History():
  def __init__(self):
    self.main_dir = os.getcwd()
    self.data = {}

  def _get_history_file_path(self, username) -> str:
    return os.path.join(self.main_dir, f"history_{username}.json")

  async def _update_or_save_data(self, novel_title: str, chapter_title: str, next_chapter_url: str, chapter_id: int, username: str, source: NovelSource):
    if (novel_title not in self.data) or (self.data[novel_title]["id"] < chapter_id):
      self.data[novel_title] = {
        "id": chapter_id,
        "last_read": datetime.now().timestamp(),
        "next_url": next_chapter_url,
        "source": source.value
      }

    async with aiofiles.open(self._get_history_file_path(username), 'w') as file:
      await file.write(json.dumps(self.data))

  def load_history(self, username):
    filepath = self._get_history_file_path(username)

    if os.path.exists(filepath):
      try:
        with open(filepath, 'r') as file:
          self.data = json.load(file)
      except Exception as e:
        print(e)

    return self

  async def save_read_history(self, novel_title: str, chapter_title: str, next_chapter_url: str, chapter_id: int, username: str = "", source: NovelSource = NovelSource.KAKUYOMU):
    await self.load_history(username)._update_or_save_data(novel_title, chapter_title, next_chapter_url, chapter_id, username, source)

    