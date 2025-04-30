import discord
import math
from typing import Callable
from discord.ui import Select, View, Button
from utils.enum import NovelSource

class ReadingHistoryView(View):
  def __init__(self, datas: list[list[str]],  continue_read_callback: Callable[[discord.Interaction, str, NovelSource], None], per_page: int=25):
    super().__init__(timeout=None)
    self.datas = datas
    self.per_page = per_page
    self.page = 0
    self.max_page = math.ceil(len(datas) / per_page) - 1
    self.selected_novel_data = ""
    self.continue_read_callback = continue_read_callback
    self.source = NovelSource.KAKUYOMU
    self.update_view()

  def update_view(self):
    self.clear_items()
    self.add_item(self.build_select())
    self.add_item(self.first_button())
    self.add_item(self.prev_button())
    self.add_item(self.next_button())
    self.add_item(self.last_button())
    self.add_item(self.continue_button())
    return self

  def build_select(self):
    start = self.page * self.per_page
    end = start + self.per_page

    options = []

    async def callback(interaction: discord.Interaction):
      try:
        # set selected novel to select values
        self.selected_novel_data = interaction.data["values"][0]

        # set selected novel to it's original data values
        self.selected_novel_data = [data for _, data in self.datas[start:end] if data.startswith(self.selected_novel_data)][0]

        # set scraping source
        self.source = NovelSource(int(self.selected_novel_data.split("|")[-2]))
        self.update_view()

        await interaction.response.edit_message(view=self)
      except Exception as e:
        print(e)

    for novel, datas in self.datas[start:end]:
      select_value_data = datas.split("|")[0:-2]

      options.append(
        discord.SelectOption(
          label=novel,
          value="|".join(select_value_data),
          default=self.selected_novel_data == datas
        )
      )

    select = Select(placeholder=f"Page {self.page + 1}", options=options)
    select.callback = callback
    return select

  def first_button(self):
    button = Button(label="First", style=discord.ButtonStyle.green)

    async def callback(interaction: discord.Interaction):
      self.page = 0
      self.update_view()
      await interaction.response.edit_message(view=self)

    button.disabled = self.page <= 0
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
    button = Button(label="Prev", style=discord.ButtonStyle.secondary)

    async def callback(interaction: discord.Interaction):
      self.page -= 1
      self.update_view()
      await interaction.response.edit_message(view=self)

    button.disabled = self.page <= 0
    button.callback = callback
    return button

  def next_button(self):
    button = Button(label="Next", style=discord.ButtonStyle.secondary)

    async def callback(interaction: discord.Interaction):
      self.page += 1
      self.update_view()
      await interaction.response.edit_message(view=self)

    button.disabled = self.page >= self.max_page
    button.callback = callback
    return button

  def continue_button(self):
    button = Button(label="Continue Reading", style=discord.ButtonStyle.blurple)

    async def callback(interaction: discord.Interaction):
      return await self.continue_read_callback(interaction, self.selected_novel_data, self.source)

    button.disabled = not self.selected_novel_data
    button.callback = callback
    return button