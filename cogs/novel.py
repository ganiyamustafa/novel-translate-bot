import discord

from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View
from utils import Scraper, TranslateOutputType
from utils.discord_ui import PaginationResultTagSelectView, NovelReadingView

class Slash(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
    self.scraper = Scraper()

  @commands.command(name="sync")
  async def sync(self, ctx) -> None:
    fmt = await self.client.tree.sync()
    await ctx.send(f"Synced {len(fmt)} commands.")

  async def _find_chapter(self, interaction: discord.Interaction, url: str):
    # await interaction.response.defer()

    # main logic
    chapters_bs4, next_tag, prev_tag = self.scraper.scrape_list_chapter(url)

    if not chapters_bs4:
      await interaction.response.send_message("Not Found")

    async def select_callback(interact: discord.Interaction):
      try:
        await self._read_story(interact, interact.data['values'][0])
      except Exception as e:
        print(e)

    view=PaginationResultTagSelectView(datas=chapters_bs4, select_callback=select_callback, next_callback_disabled=(not next_tag.name in "a"))

    async def next_callback(interaction: discord.Interaction):
      chapters_bs4, next, prev = self.scraper.scrape_list_chapter(f"https://ncode.syosetu.com/{next_tag.get('href')}")
      has_next = next.name in "a"

      if not chapters_bs4:
        await interaction.response.send_message("Not Found")

      view.page += 1
      view.next_callback_disabled=not has_next
      view.update_datas(chapters_bs4)
      view.update_view()

      await interaction.response.edit_message(view=view)

    view.next_callback = next_callback

    # scrap novel
    await interaction.response.edit_message(content="", view=view)

  async def _read_story(self, interaction: discord.Interaction, url: str):
    await interaction.response.defer()

    feedback_msg = await interaction.followup.send("Processing your request, maybe took a minute, please wait...", ephemeral=True)

    try:
      story = self.scraper.scrape_story(url)
      translated_story = self.scraper.translate(story.text)
      filtered_translated_story = [txt for txt in translated_story.split('\n')]
      story_datas = []

      print(len(filtered_translated_story))

      while filtered_translated_story:
        story_data = ""

        while len(story_data) <= 1500:
          if not filtered_translated_story:
            break

          if len(story_data) + len(filtered_translated_story[0]) > 2000:
            print("hehe", len(story_data))
            break

          story_data += f"\n{filtered_translated_story.pop(0)}"

        story_datas.append(story_data)

      view=NovelReadingView(datas=story_datas)

      await feedback_msg.edit(content=story_datas[0], view=view)
    except Exception as e:
      print(e)


  @app_commands.command(name="search", description="searching a novel")
  @app_commands.guild_only()
  async def search(self, interaction: discord.Interaction, title: str):
    await interaction.response.defer()

    # scrape data
    titles_bs4 = self.scraper.scrape_list_title(title)
    if titles_bs4:
      async def callback(interaction: discord.Interaction):
        try:
          await self._find_chapter(interaction, select.values[0])
        except Exception as e:
          print(e)

      # create ui
      select = Select(
        placeholder="Choose one option...",
        options=[discord.SelectOption(label=title.get_text(), value=title.get("href")) for title in titles_bs4],
      )
      select.callback = callback

      view = View()
      view.add_item(select)

      # scrap novel
      await interaction.followup.send(view=view, ephemeral=True)
    else:
      await interaction.followup.send("Not Found")

  @app_commands.command(name="read", description="Start reading a novel")
  @app_commands.guild_only()
  async def read(self, interaction: discord.Interaction, title: str, chapter: int):
    await interaction.response.defer()
    # scrap novel
    await interaction.followup.send("reading novel...")

async def setup(client):
    await client.add_cog(Slash(client))