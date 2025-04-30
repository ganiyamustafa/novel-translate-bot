import discord

from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View
from utils import Scraper, History
from utils.enum import NovelSource
from utils.discord_ui import PaginationResultTagSelectView, NovelReadingView, ReadingHistoryView
from datetime import datetime

class Slash(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
    self.scraper = Scraper()
    self.history = History()

  @commands.command(name="sync")
  async def sync(self, ctx) -> None:
    fmt = await self.client.tree.sync()
    await ctx.send(f"Synced {len(fmt)} commands.")

  async def _find_chapter(self, interaction: discord.Interaction, data: str, source: NovelSource = NovelSource.SYOSETSU):
    await interaction.response.defer()

    view_msg = interaction.message

    # warning waiting message
    warning_waiting_msg = await interaction.followup.send(content="maybe took a minute, please wait...", ephemeral=True)

    # main logic
    url, novel_title = data.split("|")
    chapters_bs4, next_tag, prev_tag = self.scraper.scrape_list_chapter(url, source=source)

    if not chapters_bs4:
      await interaction.response.send_message("Not Found")

    async def select_callback(interact: discord.Interaction):
      try:
        view.select.disabled = True
        await self._read_story(interact, f"{interact.data['values'][0]}|0|{novel_title}", source=source)
      except Exception as e:
        print(e)

    view=PaginationResultTagSelectView(next_tag=next_tag, prev_tag=prev_tag, datas=chapters_bs4, select_callback=select_callback, next_callback_disabled=bool(next_tag and not next_tag.name in "a"), source=source)

    async def next_callback(interaction: discord.Interaction):
      if view.next_tag:
        chapters_bs4, next, prev = self.scraper.scrape_list_chapter(view.next_tag.get('href'), source=source)
        has_next = next.name in "a"

        if not chapters_bs4:
          await interaction.response.send_message("Not Found")

        view.page += 1
        view.next_callback_disabled=not has_next
        view.update_datas(chapters_bs4)
        view.update_view()
        view.next_tag = next
        view.prev_tag = prev

        await interaction.response.edit_message(view=view)

    view.next_callback = next_callback

    # delete warning message
    try:
      await warning_waiting_msg.delete()
    except:
      pass

    # scrap novel
    await interaction.followup.edit_message(message_id=view_msg.id, content="", view=view)

  async def _read_story(self, interaction: discord.Interaction, data: str, source: NovelSource = NovelSource.SYOSETSU):
    await interaction.response.defer()

    url, ch_id, ch_title, _, novel_title = data.split("|")
    feedback_msg = await interaction.followup.send(content="Processing your request, maybe took a minute, please wait...", ephemeral=True)

    try:
      story, next_chapter, prev_chapter = self.scraper.scrape_story(url, source=source)
      translated_story = self.scraper.translate(story.text)
      filtered_translated_story = [txt for txt in translated_story.split('\n')] # break text for limit text function used
      story_datas = []

      print(len(filtered_translated_story))

      while filtered_translated_story:
        story_data = ""

        # break text if reached 2000 length and empty story data for avoid eternal loop
        if len(filtered_translated_story[0]) >= 2000 and not story_data:
          print("huhu")
          filtered_translated_story.insert(1, filtered_translated_story[0][1999:])
          filtered_translated_story[0] = filtered_translated_story[0][:1999]


        # break text for discord max limit text length
        while len(story_data) <= 1500:
          if not filtered_translated_story:
            break
          
          if len(story_data) + len(filtered_translated_story[0]) > 2000:
            print("hehe", len(story_data))
            break

          story_data += f"\n{filtered_translated_story.pop(0)}"

        story_datas.append(story_data)

      view=NovelReadingView(datas=story_datas, novel_data=data,  next_chapter_tag=next_chapter, prev_chapter_tag=prev_chapter, update_chapter_callback=self._read_story, source=source)

      await self.history.save_read_history(novel_title, ch_title, next_chapter.get("href"), ch_id, interaction.user.name, source)

      await feedback_msg.edit(content=story_datas[0], view=view)
    except Exception as e:
      print(e)


  @app_commands.command(name="search", description="searching a novel")
  @app_commands.guild_only()
  async def search(self, interaction: discord.Interaction, title: str, source: NovelSource = NovelSource.SYOSETSU):
    try:
      await interaction.response.defer()

      # scrape data
      titles_bs4 = self.scraper.scrape_list_title(title, source=source)
      if titles_bs4:
        async def callback(interaction: discord.Interaction):
          try:
            await self._find_chapter(interaction, data=select.values[0], source=source)
          except Exception as e:
            print(e)

        # create ui
        select = Select(
          placeholder="Choose one option...",
          options=[discord.SelectOption(label=title.get_text(), value=f'{title.get("href")}|{title.get_text()}') for title in titles_bs4],
        )

        select.callback = callback

        view = View()
        view.add_item(select)

        # scrap novel
        await interaction.followup.send(view=view, ephemeral=True)
      else:
        await interaction.followup.send("Not Found")
    except Exception as e:
      print(e)

  @app_commands.command(name="history", description="Get Read History")
  @app_commands.guild_only()
  async def read_history(self, interaction: discord.Interaction):
    try:
      await interaction.response.defer()

      # load history
      self.history.load_history(interaction.user.name)
      embed = discord.Embed(
        color=discord.Color.green(),
        title="Your History",
      )

      sorted_history = sorted(
        self.history.data.items(),
        key=lambda x: x[1]['last_read'],
        reverse=True
      )

      view_datas = []

      for novel_title, data in sorted_history:
        last_read = datetime.fromtimestamp(data['last_read']).strftime("%Y-%m-%d %I:%M %p")
        embed.add_field(name=f"📚 {novel_title}", value=f"\u200B\u2003\u2003📖 Chapter {data['id']} • {last_read}", inline=False)
        view_datas.append([f"{novel_title} • Chapter {data['id']}", f"{data['next_url']}|{int(data['id'])+1}|-|{data['source']}|{novel_title}"])

      view = ReadingHistoryView(datas=view_datas, continue_read_callback=self._read_story)

      await interaction.followup.send(embed=embed, view=view)
    except Exception as e:
      print(e)

  @app_commands.command(name="read", description="Start reading a novel")
  @app_commands.guild_only()
  async def read(self, interaction: discord.Interaction, title: str, chapter: int):
    await interaction.response.defer()
    # scrap novel
    await interaction.followup.send("reading novel...")

async def setup(client):
    await client.add_cog(Slash(client))