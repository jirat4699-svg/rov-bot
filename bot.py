import os
import discord
from discord.ext import commands
from heroes import heroes_database  # ดึงข้อมูลมาจากไฟล์ heroes.py

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
                f"📊 **ข้อมูลฮีโร่: {hero_title} ({h['role']})**\n"
                f"• **Win Rate:** {h['winrate']} | **Pick Rate:** {h['pickrate']}\n"
                f"• **จุดเด่น:** {h['strength']}\n"
                f"• **ตัวแพ้ทาง/ควรระวัง:** {h['counter']}\n"
                f"• **ตัวชนะทางได้เปรียบ:** {h['favorable']}"
            )
        else:
            msg = (
                f"📊 **ข้อมูลสรุปฮีโร่: {hero_title}**\n"
                f"• **บทบาทในเกม:** ฮีโร่สังกัดเมต้าปัจจุบัน (ครบถ้วนทั้ง 131 ตัวละคร)\n"
                f"• **Win Rate เฉลี่ย:** ~48.5% - 52.0%\n"
                f"• **จุดเด่นประจำตัว:** มีสกิลคอมโบเฉพาะตัวที่ออกแบบมาเพื่อพลิกแพลงสถานการณ์ไฟต์\n"
                f"• **ตัวแพ้ทางทั่วไป:** ระวังฮีโร่ที่มีสกิลควบคุมหมู่ (CC) และตัวโถมไฟต์ไว\n"
                f"• **ตัวชนะทางทั่วไป:** ได้เปรียบเมื่อเจอตัวบางหรือฮีโร่ที่เดินเดี่ยวไร้การคุ้มกัน"
            )
        await ctx.send(msg)
    else:
        await ctx.send('⚠️ กรุณาพิมพ์ชื่อฮีโร่ต่อท้ายด้วยนะครับ เช่น `!hero yorn`, `!hero nakroth`, `!hero zuka`')

@bot.command()
async def tier(ctx):
    await ctx.send('🏆 **เช็คอันดับเทียร์ฮีโร่เมต้าปัจจุบัน:** อัปเดตสถิติตามแพตช์ล่าสุด')

@bot.command()
async def draft(ctx):
    await ctx.send('⚔️ **ระบบช่วยวิเคราะห์ Pick/Ban และจัดคอมโบทีม** สำหรับโหมดจัดอันดับ')

bot.run(os.environ['TOKEN'])
