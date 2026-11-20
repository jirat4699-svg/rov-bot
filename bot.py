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
        await ctx.send(f'ข้อมูลฮีโร่ **{name}**: ค้นหาข้อมูลเชิงลึกและเทคนิคเพิ่มเติมได้ที่ https://rovlab.app')
    else:
        await ctx.send('กรุณาพิมพ์ชื่อฮีโร่ต่อท้ายด้วยนะครับ เช่น `!hero yorn` หรือดูข้อมูลทั้งหมดที่ https://rovlab.app')

@bot.command()
async def tier(ctx):
    await ctx.send('ลิงก์เช็คเทียร์ฮีโร่ล่าสุด: https://rovlab.app')

@bot.command()
async def draft(ctx):
    await ctx.send('เครื่องมือช่วยดราฟต์ฮีโร่: https://minidraft.app')

bot.run(os.environ['TOKEN'])
