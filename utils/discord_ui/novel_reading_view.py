import discord
import math
from discord.ui import Select, View, Button
from bs4 import ResultSet, Tag

class NovelReadingView(View):
  def __init__(self, datas: list[str], per_page: int=1):
    super().__init__(timeout=None)
    self.datas = datas
    self.per_page = per_page
    self.page = 0
    self.max_page = math.ceil(len(datas) / per_page) - 1
    self.update_view()

  def update_view(self):
    self.clear_items()
    self.add_item(self.prev_chapter())
    self.add_item(self.prev_button())
    self.add_item(self.next_button())
    self.add_item(self.next_chapter())
    return self

  def prev_button(self):
    button = Button(label="Prev Page", style=discord.ButtonStyle.secondary)
    has_prev_page = self.page > 0

    async def callback(interaction: discord.Interaction):
      if has_prev_page:
          self.page -= 1
          self.update_view()
          await interaction.response.edit_message(content=self.datas[self.page], view=self)

    button.disabled = not has_prev_page
    button.callback = callback
    return button

  def prev_chapter(self):
    button = Button(label="Prev Chapter", style=discord.ButtonStyle.green)

    async def callback(interaction: discord.Interaction):
      pass

    button.callback = callback
    return button

  def next_button(self):
    button = Button(label="Next Page", style=discord.ButtonStyle.secondary)
    has_prev_page = self.page < self.max_page

    async def callback(interaction: discord.Interaction):
        if has_prev_page:
          try:
            self.page += 1
            self.update_view()
            await interaction.response.edit_message(content=self.datas[self.page], view=self)
          except Exception as e:
            print(e)

    button.disabled = not has_prev_page
    button.callback = callback
    return button

  def next_chapter(self):
    button = Button(label="Next Chapter", style=discord.ButtonStyle.green)

    async def callback(interaction: discord.Interaction):
      pass

    button.callback = callback
    return button

  def update_datas(self, datas: ResultSet[Tag]):
    self.datas += datas
    self.max_page = math.ceil(len(self.datas) / self.per_page) - 1
    return self