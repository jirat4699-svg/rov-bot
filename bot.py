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
        hero_clean = name.strip().lower()
        hero_slug = hero_clean.replace(" ", "-")
        hero_title = name.title()
        
        # ตัวอย่างข้อมูลเบื้องต้นสำหรับฮีโรี้ยอดฮิต (ถ้ามีในระบบ)
        if "yorn" in hero_clean:
            msg = (
                f"🏹 **ข้อมูลฮีโร่: {hero_title} (แครี่)**\n"
                f"• **Win Rate เบื้องต้น:** ~49.5% | **Pick Rate:** สูง\n"
                f"• **จุดเด่น:** ยิงไกล ดาเมจต่อเนื่องรุนแรงท้ายเกม\n"
                f"• **ตัวแก้ทาง:** แอสซาซินที่พุ่งเข้าประชิดตัวไวๆ\n\n"
                f"🔗 **ดูสถิติตัวเต็ม รูน ไอเทม และเทคนิคทั้งหมด:**\n"
                f"https://rovlab.app/hero/{hero_slug}"
            )
        elif "nakroth" in hero_clean:
            msg = (
                f"⚡ **ข้อมูลฮีโร่: {hero_title} (ป่า / แอสซาซิน)**\n"
                f"• **Win Rate เบื้องต้น:** ~51.2% | **Pick Rate:** สูงมาก\n"
                f"• **จุดเด่น:** เคลื่อนที่ไว พลิกแพลงและแยกดันเก่ง\n"
                f"• **ตัวแก้ทาง:** ฮีโร่ที่มีสกิลล็อกเป้าหมาย (CC หนักๆ)\n\n"
                f"🔗 **ดูสถิติตัวเต็ม รูน ไอเทม และเทคนิคทั้งหมด:**\n"
                f"https://rovlab.app/hero/{hero_slug}"
            )
        else:
            # สำหรับฮีโร่ตัวอื่นๆ ทุกตัวในเกม จะสร้างข้อมูลสรุปและลิงก์ตรงให้ทันที
            msg = (
                f"📊 **ข้อมูลฮีโร่: {hero_title}**\n"
                f"• 📋 สรุปสถิติ Win Rate, รูน และไอเทมแนะนำเบื้องต้น\n\n"
                f"🔗 **คลิกดูข้อมูลเชิงลึกและเทคนิคทั้งหมดได้ที่นี่:**\n"
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
