# bot.py
import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# ดึงข้อมูลจากไฟล์ tiers.py และ draft.py
from tiers import tier_database
from draft import ModeSelectView

# --- 1. ระบบ Keep-Alive สำหรับโฮสต์บน Render ---
app = Flask('')

@app.route('/')
def home():
    return "RoV Draft Bot is Alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- 2. ตั้งค่า Discord Bot ---
intents = discord.Intents.default()
intents.message_content = True  # เปิดสิทธิ์อ่านข้อความคำสั่ง

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ บอทออนไลน์แล้วในชื่อ: {bot.user}')
    await bot.change_presence(activity=discord.Game(name="RoV | พิมพ์ !help เพื่อดูคำสั่ง"))

# --- 3. คำสั่งดู Tier List (!tier) ---
@bot.command()
async def tier(ctx, role: str = None):
    if not role:
        embed = discord.Embed(
            title="📊 ดูข้อมูล Tier List แยกตามตำแหน่ง",
            description=(
                "กรุณาพิมพ์ระบุตำแหน่งต่อท้ายคำสั่งครับ เช่น `!tier carry`\n\n"
                "**ตำแหน่งที่รองรับ:**\n"
                "• `carry` (แครี่)\n"
                "• `mage` (เมจ)\n"
                "• `jungle` (ป่า)\n"
                "• `support` (โรมมิ่ง)\n"
                "• `offlane` (ออฟเลน)"
            ),
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        return

    role_key = role.lower().strip()
    # รองรับชื่อเรียกย่อหรือคำพ้องความหมาย
    alias_map = {
        "adl": "carry", "แครี่": "carry",
        "mid": "mage", "เมจ": "mage",
        "jgl": "jungle", "ป่า": "jungle",
        "sup": "support", "roam": "support", "โรม": "support", "โรมมิ่ง": "support",
        "dsl": "offlane", "ออฟ": "offlane", "ออฟเลน": "offlane"
    }
    role_key = alias_map.get(role_key, role_key)

    if role_key in tier_database:
        embed = discord.Embed(
            description=tier_database[role_key],
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ ไม่พบตำแหน่งที่ระบุครับ ลองพิมพ์ `!tier` เพื่อดูรายชื่อตำแหน่งทั้งหมด")

# --- 4. คำสั่งกระดานจำลองการดราฟต์ (!draft) ---
@bot.command()
async def draft(ctx):
    embed = discord.Embed(
        title="🎮 เริ่มต้นกระดานจำลองการดราฟต์ (MiniDraft)",
        description="กรุณาเลือกรูปแบบกติกาที่ต้องการใช้งานด้านล่างครับ:",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed, view=ModeSelectView())

# --- 5. คำสั่งช่วยเหลือ (!help) ---
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📖 คู่มือคำสั่งบอท RoV Helper",
        description="รวมคำสั่งทั้งหมดที่ใช้งานได้ในตอนนี้ครับ:",
        color=discord.Color.green()
    )
    embed.add_field(
        name="🏆 `!draft`",
        value="เปิดกระดานจำลองการดราฟต์ฮีโร่ (เลือกได้ทั้งโหมดแข่ง Ban 4 และโหมดแรงค์ Ban 5 พร้อมระบบวิเคราะห์ผลหลังดราฟต์)",
        inline=False
    )
    embed.add_field(
        name="📊 `!tier [ตำแหน่ง]`",
        value="ดูอันดับความเก่งฮีโร่ (Tier List) เช่น `!tier carry`, `!tier jungle`, `!tier mage`, `!tier support`, `!tier offlane`",
        inline=False
    )
    await ctx.send(embed=embed)

# --- 6. เริ่มต้นการทำงาน ---
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ ERROR: ไม่พบค่า DISCORD_TOKEN ใน Environment Variables")
    else:
        bot.run(token)
