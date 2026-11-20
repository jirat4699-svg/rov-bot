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
        # แปลงชื่อเป็นตัวพิมพ์เล็กเพื่อเทียบข้อมูลตัวอย่าง
        hero_lower = name.lower()
        
        # ตัวอย่างฐานข้อมูลจำลองสถิติเบื้องต้นในบอท
        if "yorn" in hero_lower:
            msg = (
                "🏹 **ข้อมูลฮีโร่: Yorn (แครี่)**\n"
                "• **Win Rate:** 49.5% | **Pick Rate:** 18.2%\n"
                "• **จุดเด่น:** ดาเมจต่อเนื่องรุนแรงจากสกิล Passive (Farsight)\n"
                "• **ตัวแพ้ทาง/ควรระวัง:** Zill, Nakroth, Paine (ตัวไฟต์เตอร์/แอสซาซินโถมเข้าประชิดตัว)\n"
                "🔗 เช็คสถิติและเทคนิคฉบับเต็ม: https://rovlab.app/hero/yorn"
            )
        elif "nakroth" in hero_lower:
            msg = (
                "⚡ **ข้อมูลฮีโร่: Nakroth (ป่า/แอสซาซิน)**\n"
                "• **Win Rate:** 51.2% | **Pick Rate:** 22.4%\n"
                "• **จุดเด่น:** เคลื่อนที่ไวมาก ดาร์ฟ/แยกดันเก่ง พลิกแพลงสูง\n"
                "• **ตัวแพ้ทาง/ควรระวัง:** Aleister, Arum (ฮีโร่ล็อกเป้าหมาย)\n"
                "🔗 เช็คสถิติและเทคนิคฉบับเต็ม: https://rovlab.app/hero/nakroth"
            )
        else:
            msg = (
                f"📊 **ข้อมูลฮีโร่: {name.capitalize()}**\n"
                f"• ค้นหาสถิติ Win Rate, รูน, ไอเทม และตัวแก้ทางทั้งหมดได้ที่:\n"
                f"🔗 https://rovlab.app"
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
