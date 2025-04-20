# import requests
# import os


from utils.scrape import Scraper

a = Scraper()
bs = a.scrape_list_title("かませ犬から始める天下統一〜人類最高峰のラスボスを演じて原作ブレイク〜")
print(bs)

# # from groq import Groq
# from bs4 import BeautifulSoup
# from dotenv import load_dotenv

# url = "https://yomou.syosetu.com/search.php?search_type=novel&word=%E3%81%8B%E3%81%BE%E3%81%9B%E7%8A%AC%E3%81%8B%E3%82%89%E5%A7%8B%E3%82%81%E3%82%8B%E5%A4%A9%E4%B8%8B%E7%B5%B1%E4%B8%80%E3%80%9C%E4%BA%BA%E9%A1%9E%E6%9C%80%E9%AB%98%E5%B3%B0%E3%81%AE%E3%83%A9%E3%82%B9%E3%83%9C%E3%82%B9%E3%82%92%E6%BC%94%E3%81%98%E3%81%A6%E5%8E%9F%E4%BD%9C%E3%83%96%E3%83%AC%E3%82%A4%E3%82%AF%E3%80%9C&button="
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
# }

# response = requests.get(url, headers=headers)

# if response.status_code == 200:
#     html_content = response.text
# else:
#    SystemError("Failed to retrieve page")

# soup = BeautifulSoup(html_content, "html.parser")
# data = soup.select("div.searchkekka_box .novel_h")
# print(data[0].get_text())
# # filtered_text = [txt for txt in data.text.split("\n") if txt]

# # load_dotenv()
# # client = Groq(
# #     api_key=os.getenv("GROQ_KEY"),
# # )

# # translated_text = ""

# # while filtered_text:
# #   print("start again ", len(filtered_text))
# #   untranslated_text = ""

# #   while len(untranslated_text) <= 1400:
# #     if not filtered_text: 
# #       break
    
# #     untranslated_text += "\n" + filtered_text.pop(0)

# #   chat_completion = client.chat.completions.create(
# #       messages=[
# #           {
# #               "role": "user",
# #               "content": f"Terjemahkan dalam bahasa indonesia, buat agar tidak MTL \n {untranslated_text}",
# #           }
# #       ],
# #       model="deepseek-r1-distill-llama-70b",
# #   )

# #   translated_text += chat_completion.choices[0].message.content.split("</think>")[1]

# # print(translated_text)