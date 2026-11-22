# bot.py
import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# ดึงข้อมูลจากไฟล์ tiers.py และ draft.py
from tiers import tier_database
from draft import ModeSelectView, HERO_DATA

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


# --- 3. คำสั่งดูข้อมูล Tier List (!tier) ---
@bot.command()
async def tier(ctx, role: str = None):
    if not role:
        embed = discord.Embed(
            title="📊 ดูข้อมูล Tier List แยกตามตำแหน่ง",
            description=(
                "กรุณาพิมพ์ระบุตำแหน่งต่อท้ายคำสั่ง เช่น `!tier carry`\n\n"
                "**• ตำแหน่งที่รองรับ:**\n"
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
    # รองรับชื่อย่อหรือคำพ้องความหมาย
    alias_map = {
        "adl": "carry", "แคร์รี่": "carry",
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


# --- 4. คำสั่งดูข้อมูลฮีโร่รายตัว (!hero) ---
@bot.command()
async def hero(ctx, *, hero_name: str = None):
    if not hero_name:
        await ctx.send("❌ กรุณาระบุชื่อฮีโร่ด้วยครับ เช่น `!hero Nakroth` หรือ `!hero Dolia`")
        return
    
    # ค้นหาแบบไม่สนตัวพิมพ์เล็กใหญ่
    query = hero_name.strip().lower()
    matched_hero = None
    
    for h_name in HERO_DATA.keys():
        if h_name.lower() == query:
            matched_hero = h_name
            break
            
    # ถ้ายังไม่เจอแบบตรงเป๊ะ ลองหาตัวที่ขึ้นต้นด้วยหรือมีคำนั้นอยู่
    if not matched_hero:
        for h_name in HERO_DATA.keys():
            if query in h_name.lower():
                matched_hero = h_name
                break

    if matched_hero:
        data = HERO_DATA[matched_hero]
        win_rate_approx = round(48.0 + (data['score'] - 55) * 0.12, 1)
        win_rate_approx = min(max(win_rate_approx, 45.0), 55.5) # จำกัดขอบเขตสมเหตุสมผล
        
        # คำนวณข้อควรระวังตาม Tier Score
        if data['score'] >= 85:
            caution_text = "• **จุดเด่น/ข้อควรระวัง:** ตัวเมต้าความสามารถสูง สามารถหยิบเล่นได้ทุกสถานการณ์"
        elif data['score'] >= 75:
            caution_text = "• **จุดเด่น/ข้อควรระวัง:** ตัวเลือกค่อนข้างดี ต้องอาศัยความเข้าใจในการเล่นระดับหนึ่ง"
        else:
            caution_text = "• **จุดเด่น/ข้อควรระวัง:** ตัวเลือกเฉพาะทางหรือช่วงต้นเกมค่อนข้างอ่อนแอ ต้องระวังการโดนกดดัน"

        embed = discord.Embed(
            title=f"📊 ข้อมูลฮีโร่: {matched_hero}",
            description=(
                f"• **ตำแหน่งหลัก:** `{data['role']}`\n"
                f"• **ระดับ Tier:** `{data['tier']}` (คะแนนระบบ: {data['score']})\n"
                f"• **Win Rate โดยประมาณ:** `~{win_rate_approx}%`\n"
                f"{caution_text}"
            ),
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ ไม่พบข้อมูลของฮีโร่ `{hero_name}` ในระบบครับ")


# --- 5. คำสั่งกระดานจำลองการดราฟต์ (!draft) ---
@bot.command()
async def draft(ctx):
    embed = discord.Embed(
        title="🎮 เริ่มต้นกระดานจำลองการดราฟต์ (MiniDraft)",
        description="กรุณาเลือกรูปแบบกติกาที่ต้องการใช้งานด้านล่างครับ:",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed, view=ModeSelectView())


# --- 6. คำสั่งช่วยเหลือ (!help) ---
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🤖 คู่มือคำสั่งบอท RoV Helper",
        description="รวมคำสั่งทั้งหมดที่ใช้งานได้ในตอนนี้ครับ:",
        color=discord.Color.green()
    )
    embed.add_field(
        name="🎮 `!draft`",
        value="เปิดกระดานจำลองการดราฟต์ฮีโร่ (เลือกได้ทั้งโหมดแข่ง Ban 4 และโหมดแรงค์ Ban 5 พร้อมระบบวิเคราะห์ผลหลังดราฟต์)",
        inline=False
    )
    embed.add_field(
        name="📊 `!tier [ตำแหน่ง]`",
        value="ดูอันดับความเก่งฮีโร่ (Tier List) เช่น `!tier carry`, `!tier jungle`, `!tier mage`, `!tier support`, `!tier offlane`",
        inline=False
    )
    embed.add_field(
        name="🔍 `!hero [ชื่อฮีโร่]`",
        value="ดูข้อมูลและเกรดคะแนนของฮีโร่รายตัว เช่น `!hero Nakroth`, `!hero Violet`",
        inline=False
    )
    await ctx.send(embed=embed)


# --- 7. เริ่มต้นการทำงาน ---
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ ERROR: ไม่พบค่า DISCORD_TOKEN ใน Environment Variables")
    else:
        bot.run(token)
