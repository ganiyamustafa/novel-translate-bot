import discord
import math
from typing import Callable
from discord.ui import Select, View, Button
from bs4 import ResultSet, Tag

class ReadingHistoryView(View):
  def __init__(self, datas: list[list[str]], continue_read_callback: Callable[[discord.Interaction, str], None], per_page: int=25):
    super().__init__(timeout=None)
    self.datas = datas
    self.per_page = per_page
    self.page = 0
    self.max_page = math.ceil(len(datas) / per_page) - 1
    self.selected_novel_data = ""
    self.continue_read_callback = continue_read_callback
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
      self.selected_novel_data = interaction.data['values'][0]
      print(self.selected_novel_data)
      self.update_view()

      await interaction.response.edit_message(view=self)

    for novel, datas in self.datas[start:end]:
      options.append(
        discord.SelectOption(
          label=novel,
          value=datas,
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
      return await self.continue_read_callback(interaction, self.selected_novel_data)

    button.disabled = not self.selected_novel_data
    button.callback = callback
    return button