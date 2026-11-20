import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hero(ctx, *, name: str = None):
    if name:
        # จัดรูปแบบชื่อฮีโร่ให้เป็นตัวพิมพ์เล็กและแทนที่เว้นวรรคด้วยขีด (-) เพื่อให้ตรงกับลิงก์เว็บ
        hero_slug = name.strip().lower().replace(" ", "-")
        
        msg = (
            f"📊 **ข้อมูลสถิติและเทคนิคฮีโร่: {name.title()}**\n"
            f"• 🔗 ดู Win Rate, Pick Rate, รูน, ไอเทม และตัวแก้ทางทั้งหมดได้ที่:\n"
            f"https://rovlab.app/hero/{hero_slug}"
        )
        await ctx.send(msg)
    else:
        await ctx.send('⚠️ กรุณาพิมพ์ชื่อฮีโร่ต่อท้ายด้วยนะครับ เช่น `!hero yorn` หรือ `!hero nakroth`')

@bot.command()
async def tier(ctx):
    await ctx.send('🏆 **ลิงก์เช็คเทียร์ฮีโร่และเมต้าล่าสุด:** https://rovlab.app')

@bot.command()
async def draft(ctx):
    await ctx.send('⚔️ **เครื่องมือช่วยดราฟต์ฮีโร่ & วิเคราะห์ Pick/Ban:** https://minidraft.app')

bot.run(os.environ['TOKEN'])
