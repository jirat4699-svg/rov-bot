import os
import discord
from discord.ext import commands
from heroes import heroes_database

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hero(ctx, *, name: str = None):
    if name:
        hero_clean = name.strip().lower().replace(" ", "-").replace("'", "")
        hero_title = name.title()
        
        if hero_clean in heroes_database:
            h = heroes_database[hero_clean]
            msg = (
                f"📊 **{hero_title}**\n"
                f"• **Win Rate:** {h['winrate']}\n"
                f"• **ตัวแพ้ทาง/ควรระวัง:** {h['counter']}"
            )
        else:
            msg = f"⚠️ ไม่พบข้อมูลของฮีโร่ชื่อ **{hero_title}** กรุณาตรวจสอบการสะกดอีกครั้งครับ"
        await ctx.send(msg)
    else:
        await ctx.send('⚠️ กรุณาพิมพ์ชื่อฮีโร่ต่อท้ายด้วยนะครับ เช่น `!hero yorn` หรือ `!hero nakroth`')

@bot.command()
async def tier(ctx):
    await ctx.send('🏆 **เช็คอันดับเทียร์ฮีโร่เมต้าปัจจุบัน:** อัปเดตสถิติตามแพตช์ล่าสุด')

@bot.command()
async def draft(ctx):
    await ctx.send('⚔️ **ระบบช่วยวิเคราะห์ Pick/Ban และจัดคอมโบทีม**')

bot.run(os.environ['TOKEN'])
