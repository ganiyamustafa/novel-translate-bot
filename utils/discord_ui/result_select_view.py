import discord
import math
from discord.ui import Select, View, Button
from utils.enum import NovelSource
from bs4 import ResultSet, Tag

class PaginationResultTagSelectView(View):
  def __init__(self, datas: ResultSet[Tag], select_callback: callable, next_tag: Tag, prev_tag: Tag, next_callback: callable=None, source: NovelSource = NovelSource.SYOSETSU, next_callback_disabled: bool=True, per_page: int=25):
    super().__init__(timeout=None)
    self.datas = datas
    self.per_page = per_page
    self.page = 0
    self.max_page = math.ceil(len(datas) / per_page) - 1
    self.select_callback = select_callback
    self.next_callback = next_callback
    self.next_callback_disabled = next_callback_disabled
    self.source = source
    self.next_tag = next_tag
    self.prev_tag = prev_tag
    self.update_view()

  def build_select(self):
    start = self.page * self.per_page
    end = start + self.per_page

    options = []

    for chapter in self.datas[start:end]:
      if self.source == NovelSource.SYOSETSU:
        ch_id = chapter.get('href').split('/')[-2]
        
      if self.source == NovelSource.KAKUYOMU:
        ch_id = self.datas.index(chapter)+1

      options.append(
        discord.SelectOption(
          label=f"{ch_id}. {chapter.get_text(strip=True)}",
          value=f'{chapter.get("href")}|{ch_id}|None'
        )
      )

    select = Select(placeholder=f"Page {self.page + 1}", options=options)
    select.callback = self.select_callback
    return select

  def first_button(self):
    button = Button(label="First", style=discord.ButtonStyle.green)
    has_prev_page = self.page > 0

    async def callback(interaction: discord.Interaction):
      self.page = 0
      self.update_view()
      await interaction.response.edit_message(view=self)

    button.disabled = not has_prev_page
    button.callback = callback
    return button

  def last_button(self):
    button = Button(label="Last", style=discord.ButtonStyle.green)

    async def callback(interaction: discord.Interaction):
      self.page = self.max_page
      self.update_view()
      await interaction.response.edit_message(view=self)

    button.disabled = self.page >= self.max_page
    button.callback = callback
    return button

  def prev_button(self):
    button = Button(label="Previous", style=discord.ButtonStyle.secondary)
    has_prev_page = self.page > 0

    async def callback(interaction: discord.Interaction):
      self.page -= 1
      self.update_view()
      await interaction.response.edit_message(view=self)

    button.disabled = not has_prev_page
    button.callback = callback
    return button

  def next_button(self):
    button = Button(label="Next", style=discord.ButtonStyle.secondary)

    async def callback(interaction: discord.Interaction):
      self.page += 1
      self.update_view()
      await interaction.response.edit_message(view=self)

    if self.page >= self.max_page:
      print("sss ", self.next_callback_disabled)
      button.disabled = self.next_callback_disabled
      button.callback = self.next_callback
      return button

    button.disabled = self.page >= self.max_page
    button.callback = callback
    return button

  def update_view(self):
    self.clear_items()
    self.select = self.build_select()
    self.add_item(self.select)
    self.add_item(self.first_button())
    self.add_item(self.prev_button())
    self.add_item(self.next_button())
    self.add_item(self.last_button())

  def update_datas(self, datas: ResultSet[Tag]):
    self.datas += datas
    self.max_page = math.ceil(len(self.datas) / self.per_page) - 1
    return self